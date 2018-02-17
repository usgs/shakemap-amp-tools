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
NZCATWINDOW = 5*60 #number of seconds to search around in GeoNet EQ catalog

TEXT_HDR_ROWS = 16
FP_HDR_ROWS = 10

MMPS_TO_CMPS = 1/10.0

def is_geonet(filename):
    """Check to see if file is a New Zealand GNS strong motion file.

    Args:
        filename (str): Path to possible GNS V1 data file.
    Returns:
        bool: True if GNS V1, False otherwise.
    """
    line = open(filename,'rt').readline()
    if line.find('GNS Science') >= 0:
        return True
    return False

def read_geonet(filename):
    """Read New Zealand GNS V1 strong motion file.

    Args:
        filename (str): Path to possible GNS V1 data file.
        kwargs (ref): Other arguments will be ignored.
    Returns:
        Stream: Obspy Stream containing three channels of acceleration data (cm/s**2).  
    """
    trace1,offset1 = _read_channel(filename,0)
    trace2,offset2 = _read_channel(filename,offset1)
    trace3,offset3 = _read_channel(filename,offset2)

    # occasionally, geonet horizontal components are
    # identical.  To handle this, we'll set the second
    # channel to whatever isn't the first one.
    channel1 = trace1.stats['channel']
    channel2 = trace2.stats['channel']
    channel3 = trace3.stats['channel']
    if channel1 == channel2:
        if channel1 == 'HHE':
            trace2.stats['channel'] = 'HHN'
        elif channel1 == 'HHN':
            trace2.stats['channel'] = 'HHE'
        else:
            raise Exception('Could not resolve duplicate channels in %s' % trace1.stats['station'])
    if channel2 == channel3:
        if channel2 == 'HHE':
            trace3.stats['channel'] = 'HHN'
        elif channel2 == 'HHN':
            trace3.stats['channel'] = 'HHE'
        else:
            raise Exception('Could not resolve duplicate channels in %s' % trace1.stats['station'])
    
    traces = [trace1,trace2,trace3]
    stream = Stream(traces)
    return stream
    

def _read_channel(filename,line_offset):
    """Read channel data from GNS V1 text file.
    
    Args:
        filename (str): Input GNS V1 filename.
        line_offset (int): Line offset to beginning of channel text block.
    Returns:
        tuple: (obspy Trace, int line offset)
    """
    # read station and location strings from text header
    with open(filename,'rt') as f:
        for _ in range(line_offset):
            next(f)
        lines = [next(f) for x in range(TEXT_HDR_ROWS)]
        
    # parse out the station name, location, and component string
    # from text header
    station = lines[1].split()[1]
    location = lines[2].replace(' ','_').strip()
    component = lines[12].split()[1]

    # read floating point header array
    skip_header = line_offset + TEXT_HDR_ROWS
    hdr_data = np.genfromtxt(filename,skip_header=skip_header,
                             max_rows=FP_HDR_ROWS)

    # parse header dictionary from float header array
    hdr = _read_header(hdr_data,station,location,component)

    # read in the data
    if hdr['npts'] % 10 != 0:
        nrows = int(np.floor(hdr['npts']/10))
        nrows2 = 1
    else:
        nrows = int(np.ceil(hdr['npts']/10))
        nrows2 = 0
    skip_header2 = line_offset + TEXT_HDR_ROWS + FP_HDR_ROWS
    data = np.genfromtxt(filename,skip_header=skip_header2,
                         max_rows=nrows, filling_values=np.nan)
    data = data.flatten()
    if nrows2:
        skip_header3 = skip_header2 + nrows
        data2 = np.genfromtxt(filename,skip_header=skip_header3,
                              max_rows=nrows2, filling_values=np.nan)
        data = np.hstack((data,data2))
        nrows += nrows2

    
    data *= MMPS_TO_CMPS # convert to cm/s**2
    trace = Trace(data,Stats(hdr))
    offset = skip_header2 + nrows
    
    return (trace,offset)
    
def _read_header(hdr_data,station,location,component):
    """Construct stats dictionary from header lines.

    Args:
        hdr_data (ndarray): (10,10) numpy array containing header data.
        station (str): Station code obtained from previous text portion of header.
        location (str): Location string obtained from previous text portion of header.
        component (str): Component direction (N18E, S72W, etc.)
    Returns:
        Dictionary containing fields:
            - station
            - location
            - sampling_rate Samples per second.
            - delta Interval between samples (seconds)
            - calib Calibration factor (always 1.0)
            - npts Number of samples in record.
            - network "GNS"
            - units "acc"
            - source 'New Zealand Institute of Geological and Nuclear Science'
            - channel HHE,HHN,or HHZ.
            - starttime Datetime object containing start of record.
            - lat Latitude of station.
            - lon Longitude of station.

    """
    hdr = {}
    hdr['station'] = station
    hdr['location'] = location
    hdr['sampling_rate'] = hdr_data[4,0]
    hdr['delta'] = 1/hdr['sampling_rate']
    hdr['calib'] = 1.0
    hdr['npts'] = int(hdr_data[3,0])
    hdr['network'] = 'GNS'
    hdr['units'] = 'acc'
    hdr['source'] = 'New Zealand Institute of Geological and Nuclear Science'
    if component == 'Up':
        hdr['channel'] = 'HHZ'
    else:
        hdr['channel'] = _get_channel(component)

    # figure out the start time
    milliseconds = hdr_data[3,9]
    seconds = int(milliseconds/1000)
    microseconds = int(np.round(milliseconds/1000.0 - seconds))
    year = int(hdr_data[0,8])
    month = int(hdr_data[0,9])
    day = int(hdr_data[1,8])
    hour = int(hdr_data[1,9])
    minute = int(hdr_data[3,8])
    hdr['starttime'] = datetime(year,month,day,hour,minute,seconds,microseconds)

    # figure out station coordinates
    hdr['lat'] = -hdr_data[2,0] + ((hdr_data[2,1] + hdr_data[2,2]/60.0)/60.0)
    hdr['lon'] = hdr_data[2,3] + ((hdr_data[2,4] + hdr_data[2,5]/60.0)/60.0)
    
    return hdr

def _get_channel(component):
    """Determine channel name string from component string.
    
    Args:
        component (str): String like "N28E".
    
    Returns:
        str: Channel (HHE,HHN,HHZ)
    """
    compass_dict = {'N':0,'S':180}
    start_direction = component[0]
    end_direction = component[-1]
    angle = int(re.search("\\d+",component).group())
    if start_direction == 'N':
        if end_direction == 'E':
            comp_angle = angle
        else:
            comp_angle = 360-angle
    else:
        if end_direction == 'E':
            comp_angle = 180-angle
        else:
            comp_angle = 180+angle
    if comp_angle > 315 or comp_angle < 45 or comp_angle > 135 and comp_angle < 225:
        channel = 'HHN'
    else:
        channel = 'HHE'
        
    return channel
    

