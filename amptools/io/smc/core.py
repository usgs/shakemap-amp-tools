#!/usr/bin/env python

# stdlib imports
from datetime import datetime
import os
import re
import warnings

# third party
from obspy.core.trace import Trace
from obspy.core.stream import Stream
from obspy.core.trace import Stats
from obspy.core.utcdatetime import UTCDateTime
import numpy as np

ASCII_HEADER_LINES = 11
INTEGER_HEADER_LINES = 6
FLOAT_HEADER_LINES = 10
INT_HEADER_WIDTHS = 10
FLOAT_HEADER_WIDTHS = 15
DATA_COLUMNS = 8
FLOAT_DATA_WIDTHS = 10

def is_smc(filename):
    """Check to see if file is a SMC (corrected, in acc.) strong motion file.

    Args:
        filename (str): Path to possible SMC corrected data file.
    Returns:
        bool: True if DMG , False otherwise.
    """
    line = open(filename, 'rt').readline()
    if line.find('2 CORRECTED ACCELEROGRAM') > -1:
        return True
    return False

def read_smc(filename, **kwargs):
    """Read SMC strong motion file.

    Args:
        filename (str): Path to possible SMC data file.
        kwargs (ref):
            Other arguments will be ignored.
    Returns:
        Stream: Obspy Stream containing one channel of acceleration data (cm/s**2).
    """
    if not is_smc(filename):
        raise Exception('Not an SMC file.')

    stats, num_comments = _get_header_info(filename)

    skip = ASCII_HEADER_LINES + INTEGER_HEADER_LINES + \
           num_comments + FLOAT_HEADER_LINES

    # read float data (8 columns per line)
    nrows = int(np.floor(stats['npts']/DATA_COLUMNS))
    data = np.genfromtxt(filename, 
                        max_rows = nrows,
                        skip_header=skip,
                        delimiter=FLOAT_DATA_WIDTHS)
    data = data.flatten()
    if stats['npts'] % DATA_COLUMNS:
        lastrow = np.genfromtxt(filename,max_rows=1,
                                skip_header=skip+nrows,
                                delimiter=FLOAT_DATA_WIDTHS)
        data = np.append(data,lastrow)

    
    
    trace = Trace(data,header=stats)
    stream = Stream([trace])
    return stream
    
def _get_header_info(filename):
    # read the ascii header lines
    with open(filename) as f:
        ascheader = [next(f).strip() for x in range(ASCII_HEADER_LINES)]

    # station code is in the third line
    station = ''
    if len(ascheader[2]) >= 4:
        station = ascheader[2][0:4]

    station_name = ascheader[5][10:40].strip()
        
    # read integer header data
    intheader = np.genfromtxt(filename, dtype=np.int32,
                              max_rows = INTEGER_HEADER_LINES,
                              skip_header=ASCII_HEADER_LINES,
                              delimiter=INT_HEADER_WIDTHS)
    # 8 columns per line
    # first line is start time information, and then inst. serial number
    missing_data = intheader[0,0]
    year = intheader[0,1]
    jday = intheader[0,2]
    hour = intheader[0,3]
    minute = intheader[0,4]
    second = intheader[0,5]
    microsecond = 0
    if not intheader[0,6] == missing_data:
        microsecond = intheader[0,6] / 1e3 # convert milliseconds to microseconds
    datestr = '%i %00i %i %i %i %i' % (year,jday,hour,minute,second,microsecond)
    start_time = datetime.strptime(datestr,'%Y %j %H %M %S %f')

    # second line is information about number of channels, orientations
    # we care about orientations
    vertical_orientation = intheader[1,4]
    horizontal_orientation = intheader[1,5]

    # figure out the channel code
    if vertical_orientation in [0,180]:
        channel = 'Z'
    else:
        if horizontal_orientation > 0 and horizontal_orientation < 180:
            channel = 'H1'
        else:
            channel = 'H2'
    
    num_comments = intheader[1,7]

    # third line contains number of data points
    npts = intheader[2,0]
    problem_flag = intheader[2,1]
    if problem_flag == 1:
        fmt = 'Record found in file %s has a problem flag!'
        raise Exception(fmt % filename)
    structure = intheader[2,2]
    if structure != missing_data:
        fmt = 'Record found in file %s is not a free-field sensor!'
        raise Exception(fmt % filename)
    
    # station is repeated here if all numeric
    if not len(station):
        station = '%i' % intheader[3,5]

    # read float header data
    skip = ASCII_HEADER_LINES + INTEGER_HEADER_LINES
    floatheader = np.genfromtxt(filename, 
                                max_rows = FLOAT_HEADER_LINES,
                                skip_header=skip,
                                delimiter=FLOAT_HEADER_WIDTHS)

    # float headers are 10 lines of 5 floats each
    missing_data = floatheader[0,0]
    sampling_rate = floatheader[0,1]
    lat = floatheader[2,0]
    lon = floatheader[2,1]
    elev = floatheader[2,2]

    stats = {}
    
    stats['sampling_rate'] = sampling_rate
    stats['npts'] = npts
    stats['network'] = 'UK'
    stats['location'] = '--'
    stats['station'] = station
    stats['channel'] = channel
    stats['starttime'] = UTCDateTime(start_time)
    stats['units'] = 'acc'
    stats['lat'] = lat
    stats['lon'] = lon
    stats['source'] = 'Unknown'
    stats['name'] = station_name

    return (stats, num_comments)
