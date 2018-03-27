# stdlib imports
import warnings

# third party imports
import pandas as pd
import numpy as np
from obspy.signal.invsim import simulate_seismometer, corn_freq_2_paz
from obspy.core.trace import Trace
from obspy.core.stream import Stream

GAL_TO_PCTG = 1 / (9.8)

FILTER_FREQ = 0.02
CORNERS = 4


def _group_channels(streams):
    """Consolidate streams for the same event.

    Checks to see if there channels for one event in different streams, and
    groups them into one stream. Then streams are checked for duplicate
    channels (traces).

    Args:
        streams (list): List of Stream objects.
    Returns:
        list: List of Stream objects.
    """
    # Return the original stream if there is only one
    if len(streams) <=1:
        return streams

    # Get the all traces
    trace_list = []
    for stream in streams:
        for trace in stream:
            trace_list += [trace]

    # Create a list of duplicate traces and event matches
    duplicate_list = []
    match_list = []
    for idx1, trace1 in enumerate(trace_list):
        matches = []
        network = trace1.stats['network']
        station = trace1.stats['station']
        starttime = trace1.stats['starttime']
        endtime = trace1.stats['endtime']
        channel = trace1.stats['channel']
        data = np.asarray(trace1.data)
        for idx2, trace2 in enumerate(trace_list):
            if idx1 != idx2 and idx1 not in duplicate_list:
                event_match = False
                duplicate = False
                try:
                    same_data = ((data == np.asarray(trace2.data)).all())
                except AttributeError:
                    same_data = (data == np.asarray(trace2.data))
                if (
                        network == trace2.stats['network'] and
                        station == trace2.stats['station'] and
                        starttime == trace2.stats['starttime'] and
                        endtime == trace2.stats['endtime'] and
                        channel == trace2.stats['channel'] and
                        same_data
                    ):
                    duplicate = True
                elif (
                        network == trace2.stats['network'] and
                        station == trace2.stats['station'] and
                        starttime == trace2.stats['starttime'] and
                        endtime == trace2.stats['endtime']
                    ):
                    event_match = True
                if duplicate:
                    duplicate_list += [idx2]
                if event_match:
                    matches += [idx2]
        match_list += [matches]

    # Create an updated list of streams
    streams = []
    for idx, matches in enumerate(match_list):
        stream = Stream()
        grouped = False
        for match_idx in matches:
            if match_idx not in duplicate_list:
                if idx not in duplicate_list:
                    stream.append(trace_list[match_idx])
                    duplicate_list += [match_idx]
                    grouped = True
        if grouped == True:
            stream.append(trace_list[idx])
            duplicate_list += [idx]
            streams += [stream]

    # Check for ungrouped traces
    for idx, trace in enumerate(trace_list):
        if idx not in duplicate_list:
            stream = Stream()
            streams += [stream.append(trace)]
            warnings.warn('One channel stream:\n%s' %(stream), Warning)

    return streams


def get_spectral(trace, samp_rate):
    """Compute ShakeMap pseudo-spectral parameters

    Compute 5% damped PSA at 0.3, 1.0, and 3.0 seconds.

    Args:
        trace (Obspy Trace): Input trace containing acceleration (cm/s**2).
        samp_rate (int or float): Sampling rate (Hz).
    Returns:
        list: Three traces at 0.3, 1.0, and 3.0 seconds.
    """
    D = 0.05  # 5% damping

    pdict = {0.3: 'psa03',
             1.0: 'psa10',
             3.0: 'psa30'}

    traces = []
    periods = [0.3, 1.0, 3.0]
    for T in periods:
        freq = 1.0 / T
        omega = (2 * 3.14159 * freq) ** 2

        paz_sa = corn_freq_2_paz(freq, damp=D)
        paz_sa['sensitivity'] = omega
        paz_sa['zeros'] = []
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            dd = simulate_seismometer(trace.data, samp_rate, paz_remove=None,
                                      paz_simulate=paz_sa, taper=True,
                                      simulate_sensitivity=True,
                                      taper_fraction=0.05)

        stats_out = trace.stats.copy()
        stats_out['period'] = pdict[T]
        stats_out['channel'] = '%s_%s' % (
            stats_out['channel'], stats_out['period'])
        trace_out = Trace(dd, stats_out)
        traces.append(trace_out)

    return traces


def streams_to_dataframe(streams):
    """Extract peak ground motions from list of Stream objects.

    Args:
        streams (list): List of Stream objects.
    Returns:
        DataFrame: Pandas dataframe containing columns:
            - station Station code.
            - location Location string.
            - source Long form string containing source network.
            - network Short network code.
            - lat Station latitude
            - lon Station longitude
            - HHE East-west channel (or H1) (multindex with pgm columns):
                - pga Peak ground acceleration (%g).
                - pgv Peak ground velocity (cm/s).
                - psa03 Pseudo-spectral acceleration at 0.3 seconds (%g).
                - psa10 Pseudo-spectral acceleration at 1.0 seconds (%g).
                - psa30 Pseudo-spectral acceleration at 3.0 seconds (%g).
            - HHN North-south channel (or H2) (multindex with pgm columns):
                - pga Peak ground acceleration (%g).
                - pgv Peak ground velocity (cm/s).
                - psa03 Pseudo-spectral acceleration at 0.3 seconds (%g).
                - psa10 Pseudo-spectral acceleration at 1.0 seconds (%g).
                - psa30 Pseudo-spectral acceleration at 3.0 seconds (%g).
            - HHZ Vertical channel (or HZ) (multindex with pgm columns):
                - pga Peak ground acceleration (%g).
                - pgv Peak ground velocity (cm/s).
                - psa03 Pseudo-spectral acceleration at 0.3 seconds (%g).
                - psa10 Pseudo-spectral acceleration at 1.0 seconds (%g).
                - psa30 Pseudo-spectral acceleration at 3.0 seconds (%g).

    """
    # top level columns
    columns = ['station', 'location', 'source', 'network', 'lat', 'lon']

    # Check for common events and group channels
    streams = _group_channels(streams)

    # Determine which channels should be created
    channels = []
    subchannels = []
    for stream in streams:
        for trace in stream:
            if trace.stats['channel'] not in channels:
                channels.append(trace.stats['channel'])
            if not len(subchannels):
                if trace.stats['units'] == 'acc':
                    subchannels = ['pga', 'pgv', 'psa03', 'psa10', 'psa30']
                elif trace.stats['units'] == 'vel':
                    subchannels = ['pgv']
                else:
                    raise ValueError('Unknown units %s' % trace['units'])

    # Create dictionary to hold columns of basic data
    meta_dict = {}
    for column in columns:
        meta_dict[column] = []

    subcolumns = [''] * len(columns)
    subcolumns += subchannels * len(channels)

    # It's complicated to create a dataframe with a multiindex.
    # Create two arrays, one for top level columns, and another for "sub" columns.
    newchannels = []
    for channel in channels:
        newchannels += [channel] * len(subchannels)
    columns += newchannels

    dfcolumns = pd.MultiIndex.from_arrays([columns, subcolumns])
    dataframe = pd.DataFrame(columns=dfcolumns)

    # make sure we set the data types of all of the columns
    dtypes = {'station': str,
              'location': str,
              'source': str,
              'network': str,
              'lat': np.float64,
              'lon': np.float64}

    dataframe = dataframe.astype(dtypes)

    # create a dictionary for pgm data.  Because it is difficult to set columns
    # in a multiindex, we're creating dictionaries to create the channel columns
    # separately.
    channel_dicts = {}
    for channel in channels:
        channel_dicts[channel] = {}
        for subchannel in subchannels:
            channel_dicts[channel][subchannel] = []

    # loop over streams and extract data
    spectral_streams = []
    for stream in streams:
        for key in meta_dict.keys():
            meta_dict[key].append(stream[0].stats[key])
        spectral_traces = []
        for trace in stream:
            channel = trace.stats['channel']
            if trace.stats['units'] == 'acc':
                # do some basic data processing - if this has already been done,
                # it shouldn't hurt to repeat it.
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    trace.detrend('linear')
                    trace.detrend('demean')
                    trace.taper(max_percentage=0.05, type='cosine')
                    trace.filter('highpass', freq=FILTER_FREQ,
                                 zerophase=True, corners=CORNERS)
                    trace.detrend('linear')
                    trace.detrend('demean')

                # get the peak acceleration
                pga = np.abs(trace.max()) * GAL_TO_PCTG

                # get the peak velocity
                vtrace = trace.copy()
                vtrace.integrate()
                pgv = np.abs(vtrace.max())

                # get the three spectral reponses
                samp_rate = trace.stats['sampling_rate']
                trace_03, trace_10, trace_30 = get_spectral(trace, samp_rate)
                spectral_traces += [trace_03, trace_10, trace_30]

                # get the peak values from each spectral waveform,
                # convert to %g
                psa03 = np.abs(trace_03.max()) * GAL_TO_PCTG
                psa10 = np.abs(trace_10.max()) * GAL_TO_PCTG
                psa30 = np.abs(trace_30.max()) * GAL_TO_PCTG

                # assign values into dictionary
                channel_dicts[channel]['pga'].append(pga)
                channel_dicts[channel]['pgv'].append(pgv)
                channel_dicts[channel]['psa03'].append(psa03)
                channel_dicts[channel]['psa10'].append(psa10)
                channel_dicts[channel]['psa30'].append(psa30)
            else:
                # we only have a velocity channel
                pgv = np.abs(vtrace.max())
                channel_dicts[channel]['pgv'].append(pgv)
        outstream = Stream(spectral_traces)
        spectral_streams.append(outstream)

    # assign the non-channel specific stuff to dataframe
    for key, value in meta_dict.items():
        dataframe[key] = value

    # for each channel, assign peak values to dataframe
    for channel, channel_dict in channel_dicts.items():
        subdf = dataframe[channel].copy()
        for key, value in channel_dict.items():
            subdf[key] = value
        dataframe[channel] = subdf

    return (dataframe, spectral_streams)
