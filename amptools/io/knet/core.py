#!/usr/bin/env python

# stdlib imports
from datetime import datetime
import re
import os.path

# third party
from obspy.core.trace import Trace
from obspy.core.stream import Stream
from obspy.core.trace import Stats
import numpy as np

TEXT_HDR_ROWS = 17
TIMEFMT = '%Y/%m/%d %H:%M:%S'
COLS_PER_LINE = 8


def is_knet(filename):
    """Check to see if file is a Japanese KNET strong motion file.

    Args:
        filename (str): Path to possible GNS V1 data file.
    Returns:
        bool: True if GNS V1, False otherwise.
    """
    filename, _ = os.path.splitext(filename)
    knet_files = [filename + '.EW', filename + '.NS', filename + '.UD']
    results = []
    for fname in knet_files:
        if not os.path.isfile(fname):
            return False

        with open(fname, 'rt') as f:
            lines = [next(f) for x in range(TEXT_HDR_ROWS)]

        if lines[0].startswith('Origin Time') and lines[5].startswith('Station Code'):
            results.append(1)
    if sum(results) == 3:
        return True
    return False


def read_knet(filename):
    """Read Japanese KNET strong motion file.

    Args:
        filename (str): Path to possible KNET data file (extension will be ignored.)
        kwargs (ref): Other arguments will be ignored.
    Returns:
        Stream: Obspy Stream containing three channels of acceleration data (cm/s**2).
    """
    # Each KNET file contains one channel, so these files should be grouped together,
    # with .EW, .NS, .UD extensions.  We'll read in all three files here,
    # and raise an Exception if there aren't three files together.

    filename, ext = os.path.splitext(filename)
    if not is_knet(filename):
        raise Exception('%s is not a valid KNET file grouping.' % filename)
    knet_files = [filename + '.EW', filename + '.NS', filename + '.UD']
    traces = []
    for fname in knet_files:

        # Parse the header portion of the file
        with open(fname, 'rt') as f:
            lines = [next(f) for x in range(TEXT_HDR_ROWS)]

        hdr = {}
        hdr['station'] = lines[5].split()[2]
        hdr['location'] = 'unknown'
        hdr['lat'] = float(lines[6].split()[2])
        hdr['lon'] = float(lines[7].split()[2])
        hdr['sampling_rate'] = float(
            re.search('\\d+', lines[10].split()[2]).group())
        hdr['delta'] = 1 / hdr['sampling_rate']
        hdr['calib'] = 1.0
        hdr['units'] = 'acc'
        hdr['network'] = 'KNET'
        hdr['source'] = 'Japan National Research Institute for Earth Science and Disaster Resilience'
        if lines[12].split()[1] == 'N-S':
            hdr['channel'] = 'HHN'
        elif lines[12].split()[1] == 'E-W':
            hdr['channel'] = 'HHE'
        elif lines[12].split()[1] == 'U-D':
            hdr['channel'] = 'HHZ'
        else:
            raise Exception('Could not parse direction %s' %
                            lines[12].split()[1])

        scalestr = lines[13].split()[2]
        parts = scalestr.split('/')
        num = float(parts[0].replace('(gal)', ''))
        den = float(parts[1])
        calib = num / den

        duration = float(lines[11].split()[2])

        hdr['npts'] = int(duration * hdr['sampling_rate'])

        timestr = ' '.join(lines[9].split()[2:4])
        hdr['starttime'] = datetime.strptime(timestr, TIMEFMT)

        # read in the data - there is a max of 8 columns per line
        # the code below handles the case when last line has
        # less than 8 columns
        if hdr['npts'] % COLS_PER_LINE != 0:
            nrows = int(np.floor(hdr['npts'] / COLS_PER_LINE))
            nrows2 = 1
        else:
            nrows = int(np.ceil(hdr['npts'] / COLS_PER_LINE))
            nrows2 = 0
        data = np.genfromtxt(fname, skip_header=TEXT_HDR_ROWS,
                             max_rows=nrows, filling_values=np.nan)
        data = data.flatten()
        if nrows2:
            skip_header = TEXT_HDR_ROWS + nrows
            data2 = np.genfromtxt(fname, skip_header=skip_header,
                                  max_rows=nrows2, filling_values=np.nan)
            data = np.hstack((data, data2))
            nrows += nrows2

        # apply the correction factor we're given in the header
        data *= calib

        # create a Trace from the data and metadata
        trace = Trace(data.copy(), Stats(hdr.copy()))

        # to match the max values in the headers,
        # we need to detrend/demean the data (??)
        trace.detrend('linear')
        trace.detrend('demean')

        traces.append(trace)

    stream = Stream(traces)
    return stream
