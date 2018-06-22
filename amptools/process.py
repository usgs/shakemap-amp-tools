"""Helper functions for processing strong ground motion data"""
#stdlib imports
import numpy as np
from obspy.signal.util import next_pow_2
from obspy.signal.konnoohmachismoothing import konno_ohmachi_smoothing


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
        
        if (abs(trace.max()[0]) >= min_amp and abs(trace.max()[0]) <= max_amp):
            return True
        else:
            return False
        
def trim_total_window(stream, org_time, epi_dist, v_min=1.0):
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
        """
        end_time = org_time + max(120, epi_dist / v_min)
        stream.trim(endtime=end_time)
        return stream
    
def taper_total_waveform(trace, length=0.05):
        """
        Applies a Hanning taper to both ends of the total waveform at a given
        length of the record.
        
        Args:
            trace (obspy.core.trace.Trace): Trace of strong motion data.
            length (float): Decimal percentage of taper at one end.
                Default is 0.05.
                
        Returns:
            trace (obspy.core.trace.Trace) after tapering.
        """
        
        # Default tapering type is the Hanning taper
        # Apply tapering to both ends of the waveform
        # This will give the same results as the default taper in SAC
        tapered_trace = trace.taper(max_percentage=0.05, side='both')
        return tapered_trace
    
def zero_pad(trace):
        """
        Pads zeros to the end of the time series to produce a time series
        length of the nearest upper power of 2.
        
        Args:
            trace (obspy.core.trace.Trace): Trace of strong motion data.
        
        Returns:
            trace (obspy.core.trace.Trace): Trace after zero padding. 
        """
        padded_npts = int(next_pow_2(trace.stats.npts)) - 1
        padded_endtime  = (trace.stats.starttime + padded_npts / trace.stats.sampling_rate)
        padded_trace = trace.trim(endtime=padded_endtime, pad=True, fill_value=0)
        
        return padded_trace
        
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
        """
        
        phase_arrival_time = event_time + epi_dist / 7.0
        
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
        spectral_data = abs(np.fft.rfft(trace.data, n=nfft)) / nfft
        
        # Get the frequencies associated with the FFT
        freqs = np.fft.rfftfreq(nfft, 1 / trace.stats.sampling_rate) 
        
        # Konno Omachi Smoothing using 20 for bandwidth parameter
        spectral_data_smoothed = konno_ohmachi_smoothing(spectral_data.astype(float), freqs, 20)
        return spectral_data_smoothed, freqs
        
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
        """
        
        # Split the noise and signal from the trace
        signal, noise = split_signal_and_noise(trace, event_time, epi_dist)
        
        # find the number of points for the Fourier transform
        nfft = max(next_pow_2(signal.stats.npts), next_pow_2(noise.stats.npts))
        
        # Transform to frequency domain and smooth spectra using konno-ohmachi smoothing
        signal_spectra_smoothed, freqs_signal = fft_smooth(signal, nfft)
        noise_spectra_smoothed, freqs_noise = fft_smooth(noise, nfft)
        
        # remove the noise level from the spectrum of the signal window
        signal_spectra_smoothed -= noise_spectra_smoothed
        
        corner_frequencies = []
        
        # loop through each frequency and calculate the signal to noise ratio
        # At each frequency, calculate the S/N and compare to specified ratio
        # If S/N greater than ratio, found a corner frequency
        # Loop once for finding low corner...
        for i, freq in enumerate(freqs_signal):
            if (signal_spectra_smoothed[i] / noise_spectra_smoothed[i] >= ratio):
                corner_frequencies.append(freq)
                break
        
        # ...And once for finding high corner
        for i, freq in enumerate(freqs_signal):
            back_idx = len(freqs_signal)-i-1
            if (signal_spectra_smoothed[back_idx] / noise_spectra_smoothed[back_idx] >= ratio):
                corner_frequencies.append(freqs_signal[back_idx])
                break
        
        # if we reached the end without finding two corner frequencies, inadequate S/N
        if len(corner_frequencies) != 2:
            return [-1, -1]
        else:
            return corner_frequencies        

# =============================================================================
# def filter_waveform():
#     
#         # Use the corner frequencies to perform a high and low pass filter
# =============================================================================
