#!/usr/bin/env python

#stdlib imports
from datetime import datetime,timedelta
import sys
import os.path
import re

#third party
from obspy.core.trace import Trace
from obspy.core.stream import Stream
from obspy.core.trace import Stats
from obspy.core.utcdatetime import UTCDateTime
import numpy as np

TIMEFMT = '%Y-%m-%dT%H:%M:%S'

TEXT_HDR_ROWS = 14
INT_HDR_ROWS = 10
FLT_HDR_ROWS = 20
COMMENT_ROWS = 4

CORRECTED_MARKER = 'CORRECTED ACCELER'

UNITS = {1:'acc',
         2:'vel'}

def is_cosmos(filename):
    """Check to see if file is a COSMOS V2 strong motion file.

    Args:
        filename (str): Path to possible COSMOS VX data file.
    Returns:
        bool: True if COSMOS V2, False otherwise.
    """
    line = open(filename,'rt').readline()
    if line.lower().find(CORRECTED_MARKER.lower()) >= 0:
        return True
    return False

def read_cosmos(filename):
    """Read COSMOS V2 strong motion file.

    Args:
        filename (str): Path to possible COSMOS V2 data file.
        kwargs (ref): Other arguments will be ignored.
    Returns:
        Stream: Obspy Stream containing three channels of acceleration data (cm/s**2).  
    """
    trace1,line_offset = _read_channel(filename,0)
    trace2,line_offset = _read_channel(filename,line_offset)
    trace3,line_offset = _read_channel(filename,line_offset)
    stream = Stream([trace1,trace2,trace3])
    return stream
    
def _read_channel(filename,line_offset):
    # station code line 4
    with open(filename,'rt') as f:
        for _ in range(line_offset):
            next(f)
        lines = [next(f) for x in range(TEXT_HDR_ROWS)]
        
    hdr = {}
    station_str = lines[4].split(':')[2].split()[0].strip()
    hdr['network'],hdr['station'] = station_str.split('-')
    locparts = lines[4].split(':')[2].split()[1:]
    hdr['location'] = '_'.join(locparts)

    # read in 10 lines of integer data
    int_data = np.genfromtxt(filename,
                             skip_header=line_offset + TEXT_HDR_ROWS,
                             max_rows=INT_HDR_ROWS).flatten().astype(np.int32)
    skiprows = line_offset + TEXT_HDR_ROWS + INT_HDR_ROWS + 1
    flt_data = np.genfromtxt(filename,
                             skip_header=skiprows,
                             max_rows=FLT_HDR_ROWS).flatten()
    
    hdr['units'] = UNITS[int_data[1]]
    hdr['lat'] = flt_data[0]
    hdr['lon'] = flt_data[1]
    year = int_data[39]
    month = int_data[41]
    day = int_data[42]
    hour = int_data[43]
    minute = int_data[44]
    seconds = flt_data[29]
    microseconds = int((seconds - int(seconds))*1e6)
    hdr['starttime'] = datetime(year,month,day,hour,minute,int(seconds),microseconds)
    hdr['delta'] = flt_data[33]
    hdr['sampling_rate'] = 1/hdr['delta']
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
    skip_header = line_offset + TEXT_HDR_ROWS + INT_HDR_ROWS + 1 + FLT_HDR_ROWS + COMMENT_ROWS
    nrows = int(hdr['npts']/COLS_PER_LINE)
    
    data = np.genfromtxt(filename,skip_header=skip_header,
                         max_rows=nrows).flatten()
    trace = Trace(data.copy(),Stats(hdr.copy()))
    new_offset = line_offset + TEXT_HDR_ROWS + INT_HDR_ROWS + 1 + \
                 FLT_HDR_ROWS + COMMENT_ROWS + nrows

    new_offset += 1 # there is an 'end of record' line after the data
    return (trace,new_offset)
