"""Helper functions for processing strong ground motion data"""

# stdlib imports
import numpy as np
import warnings

# third party imports
from obspy.signal.util import next_pow_2
from obspy.signal.konnoohmachismoothing import konno_ohmachi_smoothing
from scipy.optimize import curve_fit


def filter_detrend(trace, taper_type='cosine', taper_percentage=0.05,
                   filter_type='highpass', filter_frequency=0.02,
                   filter_zerophase=True, filter_corners=4):
        """
        Read files from a directory and return stream objects.

        Args:
            trace (obspy.core.trace.Trace): Trace of strong motion data.
            taper_type (str): Type of taper used for processing.
                Default is 'cosine'.
            taper_percentage (float): Maximum taper percentage.
                Default is 0.05.
            filter_type (str): Type of filter used for processing.
                Default is 'highpass'.
            filter_frequency (float): Filter corner frequency.
                Default is 0.02.
            filter_zerophase (bool): If True, applies a forward and backward
                filter. Results in a zero phase shift. Default is True.
            filter_corners (int): Filter corners / order.

        Returns:
            list : List of obspy.core.stream.Stream objects
        """
        trace.detrend('linear')
        trace.detrend('demean')
        trace.taper(max_percentage=taper_percentage, type=taper_type)
        trace.filter(filter_type, freq=filter_frequency,
                     zerophase=filter_zerophase, corners=filter_corners)
        trace.detrend('linear')
        trace.detrend('demean')
        return trace


def correct_baseline_mean(stream):
    """
    Performs a zero-order baseline correction by subtracting the mean from
    the entire waveform. This is step 1 as found in the Rennolet et. al
    paper (https://doi.org/10.1193/101916EQS175DP)

    Args:
        stream (obpsy.core.stream.Stream): Stream of raw waveform data.

    Returns:
        stream (obspy.core.stream.Stream): Stream of corrected waveform data.
    """
    for tr in stream:
        tr.detrend(type='demean')
    return stream


def remove_clipped(stream, max_count=2000000):
    """
    Identify clipped waveforms having a count greater than the specified
    max count. This will remove any clipped waveforms from the stream.
    This is step 2 as found in the Rennolet et. al paper
    (https://doi.org/10.1193/101916EQS175DP)

    Args:
        stream (obspy.core.stream.Stream): Stream of raw data.
        max_count (int): Maximum count for clipping.

    Returns:
        stream (obspy.core.stream.Stream): Stream of raw data with clipped
        waveforms removed
    """
    for tr in stream:
        if tr.max() >= max_count:
            stream.traces.remove(tr)
            warnings.warn('Clipped trace was removed from the stream')
            warnings.warn(tr.get_id())
    return stream


def check_max_amplitude(trace, min_amp=10e-9, max_amp=50):
        """
        Checks that the maximum amplitude of the trace is within a defined
        range.

        Args:
            trace (obspy.core.trace.Trace): Trace of strong motion data.
            min_amp (float): Minimum amplitude for the acceptable range.
                Default is 10e-9.
            max_amp (float): Maximum amplitude for the acceptable range.
                Default is 50.

        Returns:
            bool: True if trace passes the check. False otherwise.
        """

        if (abs(trace.max()) >= min_amp and abs(trace.max()) <= max_amp):
            return True
        else:
            return False


def trim_total_window(trace, org_time, epi_dist, v_min=1.0):
        """
        Trims a stream of traces to the window using the algorithm
        defined in the Rennolet data paper.

        Args:
            stream (obspy.core.stream.Stream): Stream of strong motion data.
            org_time (UTCDateTime): Event origin time.
            epi_dist (float): Distance from event epicenter to station.
            v_min (float): Minimum apparent velocity.
                Default is 1.0 km/s.

        Returns:
            stream (obspy.core.stream.Stream) after windowing.
            If trim failure occurs: -1
        """

        end_time = org_time + max(120, epi_dist / v_min)

        # Check to make sure that the trimming end time is after
        # the start time of our trace
        if (end_time <= trace.stats.starttime):
            return -1
        else:
            trace.trim(endtime=end_time)
            return trace


def zero_pad(trace):
        """
        Pads zeros to the end of the time series to produce a time series
        length of the nearest upper power of 2.

        Args:
            trace (obspy.core.trace.Trace): Trace of strong motion data.

        Returns:
            trace (obspy.core.trace.Trace): Trace after zero padding.
        """

        pad_npts = int(next_pow_2(trace.stats.npts)) - 1
        pad_tim = trace.stats.starttime + pad_npts / trace.stats.sampling_rate
        trace.trim(endtime=pad_tim, pad=True, fill_value=0)
        return trace


def split_signal_and_noise(trace, event_time, epi_dist):
        """
        Identifies the noise and signal windows for the waveform.
        The noise window is defined from the start of the waveform through the
        arrival time of a 7 km/s phase. The signal window is defned from the
        arrival time of a 7 km/s phase through the end of the waveform.

        Args:
            trace (obspy.core.trace.Trace): Trace of strong motion data.
            event_time (UTCDateTime): Event origin time.
            epi_dist (float): Distance form event epicenter to station.

        Returns:
            tuple of two traces:
                1) Noise trace
                2) Signal trace
            If cannot separate noise/signal, returns -1.
        """

        # Calculate the arrival time of a 7 km/s phase
        phase_arrival_time = event_time + epi_dist / 7.0

        # Check if the arrival time is before or after the trace window
        if (phase_arrival_time <= trace.stats.starttime):
            return (-1, -1)
        elif (phase_arrival_time >= trace.stats.endtime):
            return (-1, -1)
        else:
            orig_trace_1 = trace.copy()
            orig_trace_2 = trace.copy()

        noise_trace = orig_trace_1.trim(endtime=phase_arrival_time)
        signal_trace = orig_trace_2.trim(starttime=phase_arrival_time)

        return (signal_trace, noise_trace)


def fft_smooth(trace, nfft):
        """
        Pads a trace to the nearest upper power of 2, takes the FFT, and
        smooths the ampltidue spectra following the algorithm of
        Konno and Ohmachi.

        Args:
            trace (obspy.core.trace.Trace): Trace of strong motion data.
            nfft (int): Number of data points for the fourier transform.

        Returns:
            numpy.ndarray: Smoothed amplitude data.
        """

        # Compute the FFT, normalizing by the number of data points
        spec = abs(np.fft.rfft(trace.data, n=nfft)) / nfft

        # Get the frequencies associated with the FFT
        freqs = np.fft.rfftfreq(nfft, 1 / trace.stats.sampling_rate)

        # Konno Omachi Smoothing using 20 for bandwidth parameter
        spec_smooth = konno_ohmachi_smoothing(spec.astype(float), freqs, 20)
        return spec_smooth, freqs


def get_corner_frequencies(trace, event_time, epi_dist, ratio=3.0):
        """
        Returns the corner frequencies for a trace.

        Args:
            trace (obspy.core.trace.Trace): Trace of strong motion data.
            event_time (UTCDateTime): Event origin time.
            epi_dist (float): Distance from event epicenter to station.
            ratio (float): Required signal-to-noise ratio.

        Returns:
            list : List of floats representing corner frequencies.
            Returns two -1 values if inadequate signal to noise ratio.
        """

        # Split the noise and signal into two separate traces
        signal, noise = split_signal_and_noise(trace, event_time, epi_dist)

        # Check if signal and noise splitting failed
        if (signal == -1 and noise == -1):
            return [-1, -1]

        # find the number of points for the Fourier transform
        nfft = max(next_pow_2(signal.stats.npts), next_pow_2(noise.stats.npts))

        # Transform to frequency domain and smooth spectra using
        # konno-ohmachi smoothing
        sig_spec_smooth, freqs_signal = fft_smooth(signal, nfft)
        noise_spec_smooth, freqs_noise = fft_smooth(noise, nfft)

        # remove the noise level from the spectrum of the signal window
        sig_spec_smooth -= noise_spec_smooth

        # loop through each frequency and calculate the signal to noise ratio
        # If S/N greater than ratio, found a corner frequency
        # Loop once for finding low corner...
        corner_frequencies = []
        for i, freq in enumerate(freqs_signal):
            if (sig_spec_smooth[i] / noise_spec_smooth[i] >= ratio):
                corner_frequencies.append(freq)
                break

        # ...And once for finding high corner
        for i, freq in enumerate(freqs_noise):
            idx = len(freqs_signal)-i-1  # Looping backwards through freqs
            if (sig_spec_smooth[idx] / noise_spec_smooth[idx] >= ratio):
                corner_frequencies.append(freqs_signal[idx])
                break

        # if we reached the end without finding two corner frequencies
        # inadequate S/N
        if len(corner_frequencies) != 2:
            return [-2, -2]
        else:
            return corner_frequencies


def filter_waveform_high_low(trace, high_pass_freq, low_pass_freq):
        """
        Returns the filtered waveform using the provided corner frequencies.

        Args:
            trace (obspy.core.trace.Trace): Trace of strong motion data.
            corners (list of floats): Corner frequencies.

        Returns:
            trace (obspy.core.trace.Trace): Filtered trace
        """

        # Find the Nyquist frequency, which is half the sampling rate
        nyquist_freq = 0.5 * trace.stats.sampling_rate

        trace.filter('highpass', freq=high_pass_freq, zerophase=True)

        # Only perform low pass frequency if corner is less than nyquist freq
        if (low_pass_freq < nyquist_freq):
            trace.filter('lowpass', freq=low_pass_freq, zerophase=True)
        else:
            warnings.warn('Low pass frequency is greater than or equal '
                          'to the Nyquist frequency. Low pass filter will '
                          'not be applied.')
        return trace


def poly_func(x, a, b, c, d, e):
        """
        Model polynomial function for polynomial baseline correction.
        """
        return a*x**6 + b*x**5 + c*x**4 + d*x**3 + e*x**2


def correct_baseline(trace):
        """
        Performs a baseline correction following the method of Ancheta
        et al. (2013). This removes low-frequency, non-physical trends
        that remain in the time series following filtering.

        Args:
            trace (obspy.core.trace.Trace): Trace of strong motion data.

        Returns:
            trace (obspy.core.trace.Trace): Baseline-corrected trace.
        """

        # Make copies of the trace for our accleration data
        orig_trace = trace.copy()
        acc_trace = trace.copy()

        # Integrate twice to get the displacement time series
        disp_trace = (acc_trace.integrate()).integrate()

        # Fit a sixth order polynomial to displacement time series, requiring
        # that the 1st and 0th order coefficients are zero
        time_values = np.linspace(0, trace.stats.npts-1, trace.stats.npts)
        poly_cofs = list(curve_fit(poly_func, time_values, disp_trace.data)[0])
        poly_cofs += [0, 0]

        # Construct a polynomial from the coefficients and compute
        # the second derivative
        polynomial = np.poly1d(poly_cofs)
        polynomial_second_derivative = np.polyder(polynomial, 2)

        # Subtract the second derivative of the polynomial from the
        # acceleration trace
        for i in range(orig_trace.stats.npts):
            orig_trace.data[i] -= polynomial_second_derivative(i)

        return trace


def process_all(trace, event_time, epi_dist):
    """
    Processes an acceleration trace following the step-by-step process
    described in the Rennolet et al paper
    (https://doi.org/10.1193/101916EQS175DP)
    This function completes
    Step 4 through Step 11 from the paper.

    4) Check Amplitude
    5) Window Signals
    6) Taper Total Waveform
    7) Zero-Pad Time Series
    8) Identify Corner Frequencies for High- and Low-Pass Filtering
    9) Filter Waveform
    10) Remove Zero Padding
    11) Correct Baseline

    Steps 1-3 would likely be covered in a fetcher / request script
    and Steps 13-14 in calculations of strong ground motion parameters.

    Along with trace data, this function requires two pieces of metadata:
    origin time of the event, and epicentral distance to the station.

    Args:
        trace (obspy.core.trace.Trace): Trace of strong motion data.
        event_time (UTCDateTime): Origin time of the event.
        epi_dist (float): Epicentral distance.

    Returns:
        trace (obspy.core.trace.Trace): Processed trace. If processing
        fails, then the original trace is returned.
    """

    trace_copy = trace.copy()
    trace_info = trace.stats.network + '_' + trace.stats.station + '_'
    trace_info += trace.stats.channel + '_' + str(trace.stats.starttime)

    # Step 4 - Check amplitude
    if not check_max_amplitude(trace_copy):
        warnings.warn('Trace maximum amplitude is not within the '
                      'acceptable range. ' + trace_info)
        return

    # Step 5 - Window signal
    trace_trim = trim_total_window(trace_copy, event_time, epi_dist)

    # Check if windowing failed
    if (trace_trim == -1):
        warnings.warn('Invalid time windowing. The start time of the trace '
                      'is after the calculated end time. ' + trace_info)
        return

    # Step 6 - Taper
    trace_tap = trace_trim.taper(max_percentage=0.05, side='both')

    # Step 7 - Zero pad
    before_padding_endtime = trace_tap.stats.endtime
    trace_pad = zero_pad(trace_tap)

    # Step 8 - Corner frequencies
    corners = get_corner_frequencies(trace_pad, event_time, epi_dist)

    # Check if corner frequency calculation failed
    if (corners == [-1, -1]):
        warnings.warn('Not enough pre-event noise to calculate signal '
                      'to noise ratio. ' + trace_info)
        return
    if (corners == [-2, -2]):
        warnings.warn('Signal-to-noise ratio is not high enough to '
                      'to find corner-frequencies. ' + trace_info)
        return

    high_freq = corners[0]
    low_freq = corners[1]

    # Step 9 - Filter
    trace_filt = filter_waveform_high_low(trace_pad, high_freq, low_freq)

    # Step 10 - Remove zero pad
    trace_filt.trim(endtime=before_padding_endtime)

    # Step 11 - Correct baseline
    trace_cor = correct_baseline(trace_filt)

    return trace_cor
