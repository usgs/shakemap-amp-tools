#!/usr/bin/env python

# stdlib imports
from datetime import datetime
import re

# third party
from obspy.core.trace import Trace
from obspy.core.stream import Stream
from obspy.core.trace import Stats
import numpy as np

TEXT_HDR_ROWS = 14

VALID_MARKERS = ['CORRECTED ACCELERATION',
    'UNCORRECTED ACCELERATION'
]

UNITS = {1: 'acc',
         2: 'vel'}


def is_cosmos(filename):
    """Check to see if file is a COSMOS V0/V1 strong motion file.

    Args:
        filename (str): Path to possible COSMOS V0/V1 data file.
    Returns:
        bool: True if COSMOS V0/V1 , False otherwise.
    """
    line = open(filename, 'rt').readline()
    for marker in VALID_MARKERS:
        if line.lower().find(marker.lower()) >= 0:
            if line.lower().find('(format v') >= 0:
                return True
    return False


def read_cosmos(filename, **kwargs):
    """Read COSMOS V0/V1 strong motion file.

    There is one extra key in the Stats object for each Trace - "process_level".
    This will be set to either "V0" or "V1".

    Args:
        filename (str): Path to possible COSMOS V0/V1 data file.
        kwargs (ref):
            valid_station_types (list): List of valid station types. See table
                6  in the COSMOS strong motion data format documentation for
                station type codes.
            Other arguments will be ignored.
    Returns:
        Stream: Obspy Stream containing three channels of acceleration data (cm/s**2).
    """
    # get list of valid stations
    valid_station_types = kwargs.get('valid_station_types', None)

    # count the number of lines in the file
    with open(filename) as f:
        line_count = sum(1 for _ in f)

    # read as many channels as are present in the file
    line_offset = 0
    stream = Stream([])
    while line_offset < line_count:
        trace, line_offset = _read_channel(filename, line_offset)
        # store the trace if the station type is in the valid_station_types list
        # or store the trace if there is no valid_station_types list
        if valid_station_types is not None:
            print(trace.stats['station_type'])
            if trace.stats['station_type'] in valid_station_types:
                stream.append(trace)
        else:
            stream.append(trace)

    return stream


def _read_channel(filename, line_offset):
    """Read channel data from COSMOS V0/V1 text file.

    Args:
        filename (str): Input COSMOS V0/V1 filename.
        line_offset (int): Line offset to beginning of channel text block.
    Returns:
        tuple: (obspy Trace, int line offset)
    """
    # read station, location, and process level from text header
    with open(filename, 'rt') as f:
        for _ in range(line_offset):
            next(f)
        lines = [next(f) for x in range(TEXT_HDR_ROWS)]

    # parse out the station name, location, and process level
    hdr = {}
    station_str = lines[4][lines[4].lower().find('code:'):].split(':')
    station_info = station_str[1].split('-')
    hdr['network'] =  station_info[0]
    hdr['station'] = station_info[1][0:station_info[1].find(' ')]
    locparts = lines[4].split(':')[2].split()[1:]
    hdr['name'] = '_'.join(locparts)
    if lines[0].lower().find('uncorrected') >= 0:
        hdr['process_level'] = 'V0'
    if lines[0].lower().find('corrected') >= 0:
        hdr['process_level'] = 'V1'

    # read in lines of integer data
    skiprows = line_offset + TEXT_HDR_ROWS
    int_lines, int_data = _read_lines(skiprows, filename)
    int_data = int_data.astype(np.int32)

    # read in lines of float data
    skiprows += int_lines + 1
    flt_lines, flt_data = _read_lines(skiprows, filename)

    # read in comment lines
    skiprows += flt_lines + 1
    cmt_lines, cmt_data = _read_lines(skiprows, filename)
    skiprows += cmt_lines + 1

    # according to the powers that defined the Network.Station.Channel.Location
    # "standard", Location is a two character field.  Most data providers,
    # including KNET here, don't provide this.  We'll flag it as "--".
    hdr['location'] = '--'
    
    # set statistics
    hdr['processing_comments'] = cmt_data
    hdr['units'] = UNITS[int_data[1]]
    hdr['station_type'] = int_data[18]
    hdr['lat'] = flt_data[0]
    hdr['lon'] = flt_data[1]
    year = int_data[39]
    month = int_data[41]
    day = int_data[42]
    hour = int_data[43]
    minute = int_data[44]
    seconds = flt_data[29]
    microseconds = int((seconds - int(seconds)) * 1e6)
    hdr['starttime'] = datetime(
        year, month, day, hour, minute, int(seconds), microseconds)
    hdr['delta'] = flt_data[33]
    hdr['sampling_rate'] = 1 / hdr['delta']
    duration = flt_data[34]
    hdr['npts'] = int(hdr['sampling_rate'] * duration)
    hdr['source'] = hdr['network']
    angle = int_data[53]
    if angle >= 400:
        hdr['channel'] = 'HHZ'
    elif angle > 315 or angle < 45 or (angle > 135 and angle < 225):
        hdr['channel'] = 'HHN'
    else:
        hdr['channel'] = 'HHE'

    # read in the data
    nrows, data = _read_lines(skiprows, filename)
    trace = Trace(data.copy(), Stats(hdr.copy()))

    # set new offset
    new_offset = skiprows + nrows
    new_offset += 1  # there is an 'end of record' line after the data

    return (trace, new_offset)


def _read_lines(skip_rows, filename):
    """Read lines of comments and data exluding headers.

    Args:
        skip_rows (int): Number of rows to skip.
        filename (str): Path to possible COSMOS V0/V1 data file.
    Returns:
        array-like: List of comments or array of data.
    """
    # read the headers
    header = np.genfromtxt(filename,
                               skip_header= skip_rows - 1,
                               max_rows=1,
                               dtype='str')

    # parse the number of points and convert the header to a string
    npts = int(header[0])
    header = np.array_str(header).lower().replace("'", '').replace(' ', '').lower()

    # determine whether the following lines are comments or data
    if header.lower().find('comment') >= 0:
        num_lines = npts

        # read and store comment lines
        with open(filename, 'rt') as f:
            file = f.readlines()
        max_lines = skip_rows + num_lines
        comment = [file[idx] for idx in range(skip_rows, max_lines)]
        data_arr = comment
    else:
        # parse out the format of the data
        format_data = re.findall('\d+', header[header.find('format=') + 8:])
        cols = int(format_data[0])
        fmt = int(format_data[1])
        num_lines = int(np.ceil(npts / cols))
        widths = [fmt] * cols

        # read data
        data_arr = np.genfromtxt(filename, skip_header=skip_rows,
                                     max_rows=num_lines, dtype=np.float64,
                                     delimiter=widths).flatten()
    return num_lines, data_arr
