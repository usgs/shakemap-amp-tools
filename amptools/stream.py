# stdlib imports
import warnings

# third party imports
import pandas as pd
import numpy as np
from obspy.signal.invsim import simulate_seismometer, corn_freq_2_paz
from obspy.core.trace import Trace
from obspy.core.stream import Stream

# local imports
from amptools.process import filter_detrend
from pgm.station_summary import StationSummary


GAL_TO_PCTG = 1 / (9.8)

FILTER_FREQ = 0.02
CORNERS = 4


def group_channels(streams):
    """Consolidate streams for the same event.

    Checks to see if there are channels for one event in different streams, and
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
                        starttime == trace2.stats['starttime']
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


def streams_to_dataframe(streams):
    """Extract peak ground motions from list of Stream objects.

    Args:
        streams (list): List of Stream objects.
    Returns:
        DataFrame: Pandas dataframe containing columns:
            - station Station code.
            - name Text description of station.
            - location Two character location code.
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
    columns = ['station', 'name', 'source', 'netid', 'lat', 'lon']

    # Check for common events and group channels
    streams = group_channels(streams)

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
              'name': str,
              'source': str,
              'netid': str,
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
            if key == 'name':
                try:
                    name_str = stream[0].stats['standard']['station_name']
                except KeyError:
                    name_str = stream[0].stats['name']
                meta_dict[key].append(name_str)
            elif key == 'lat':
                try:
                    latitude = stream[0].stats['coordinates']['latitude']
                except KeyError:
                    latitude = stream[0].stats['lat']
                meta_dict[key].append(latitude)
            elif key == 'lon':
                try:
                    longitude = stream[0].stats['coordinates']['longitude']
                except KeyError:
                    longitude = stream[0].stats['lon']
                meta_dict[key].append(longitude)
            else:
                if key == 'netid':
                    statskey = 'network'
                else:
                    statskey = key
                meta_dict[key].append(stream[0].stats[statskey])
        spectral_traces = []
        # process acceleration and store velocity traces
        for idx, trace in enumerate(stream):
            channel = trace.stats['channel']
            if trace.stats['units'] == 'acc':
                # do some basic data processing - if this has already been done,
                # it shouldn't hurt to repeat it.
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    stream[idx] = filter_detrend(trace, taper_type='cosine',
                            taper_percentage=0.05, filter_type='highpass',
                            filter_frequency=FILTER_FREQ,
                            filter_zerophase=True, filter_corners=CORNERS)
            elif trace.stats['units'] == 'vel':
                # we only have a velocity channel
                pgv = np.abs(trace.max())
                channel_dicts[channel]['pgv'].append(pgv)
        # get station summary and assign values
        station = StationSummary(stream, ['channels'],
                ['pga', 'pgv', 'sa0.3', 'sa1.0', 'sa3.0'])
        for channel in channels:
            pga = station.pgms['PGA'][channel]
            pgv = station.pgms['PGV'][channel]
            psa03 = station.pgms['SA0.3'][channel]
            psa10 = station.pgms['SA1.0'][channel]
            psa30 = station.pgms['SA3.0'][channel]

            spectral_traces += [station.oscillators['SA0.3'],
                    station.oscillators['SA1.0'],
                    station.oscillators['SA3.0']]

            # assign values into dictionary
            channel_dicts[channel]['pga'].append(pga)
            channel_dicts[channel]['pgv'].append(pgv)
            channel_dicts[channel]['psa03'].append(psa03)
            channel_dicts[channel]['psa10'].append(psa10)
            channel_dicts[channel]['psa30'].append(psa30)
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
