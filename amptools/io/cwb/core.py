from collections import OrderedDict
from datetime import datetime, timedelta

# third party imports
import numpy as np
from obspy.core.trace import Trace
from obspy.core.trace import Stats
from obspy.core.stream import Stream


DATE_FMT = '%Y/%m/%d-%H:%M:%S.%f'

GMT_OFFSET = 8 * 3600  # CWB data is in local time, GMT +8

HDR_ROWS = 22
COLWIDTH = 10
NCOLS = 4


def is_cwb(filename):
    """Check to see if file is a Taiwan Central Weather Bureau strong motion file.

    Args:
        filename (str): Path to possible CWB data file.
    Returns:
        bool: True if CWB, False otherwise.
    """
    f = open(filename, 'rt')
    line = f.readline()
    f.close()
    if line.startswith('#Earthquake Information'):
        return True
    return False


def read_cwb(filename, **kwargs):
    """Read Taiwan Central Weather Bureau strong motion file.

    Args:
        filename (str): Path to possible CWB data file.
        kwargs (ref): Other arguments will be ignored.
    Returns:
        Stream: Obspy Stream containing three channels of acceleration data (cm/s**2).
    """
    if not is_cwb(filename):
        raise ValueError('%s is not a valid CWB strong motion data file.')
    f = open(filename, 'rt')
    hdr = OrderedDict()
    
    # according to the powers that defined the Network.Station.Channel.Location
    # "standard", Location is a two character field.  Most data providers,
    # including CWB here, don't provide this.  We'll flag it as "--".
    hdr['location'] = '--' 
    while True:
        line = f.readline()
        if line.startswith('#StationCode'):
            hdr['station'] = line.split(':')[1].strip()
        if line.startswith('#StationName'):
            hdr['name'] = line.split(':')[1].strip()
        if line.startswith('#StationLongitude'):
            hdr['lon'] = float(line.split(':')[1].strip())
        if line.startswith('#StationLatitude'):
            hdr['lat'] = float(line.split(':')[1].strip())
        if line.startswith('#StartTime'):
            timestr = ':'.join(line.split(':')[1:]).strip()
            hdr['starttime'] = datetime.strptime(timestr, DATE_FMT)
        if line.startswith('#RecordLength'):
            hdr['duration'] = float(line.split(':')[1].strip())
        if line.startswith('#SampleRate'):
            hdr['sampling_rate'] = int(line.split(':')[1].strip())
        if line.startswith('#Data'):
            break

    data = np.genfromtxt(filename, skip_header=HDR_ROWS,
                         delimiter=[COLWIDTH] * NCOLS)  # time, Z, NS, EW
    nrows, _ = data.shape
    f.close()

    # correct start time to GMT
    hdr['starttime'] = hdr['starttime'] - timedelta(seconds=GMT_OFFSET)

    # Add some optional information to the header
    hdr['network'] = 'CWB'
    hdr['delta'] = 1 / hdr['sampling_rate']
    hdr['calib'] = 1.0
    hdr['units'] = 'acc'  # cm/s**2
    hdr['source'] = 'Taiwan Central Weather Bureau'
    hdr['npts'] = nrows
    secs = int(data[-1, 0])
    microsecs = int((data[-1, 0] - secs) * 1e6)
    hdr['endtime'] = hdr['starttime'] + \
        timedelta(seconds=secs, microseconds=microsecs)

    hdr_hhz = hdr.copy()
    hdr_hhz['channel'] = 'HHZ'

    hdr_hhe = hdr.copy()
    hdr_hhe['channel'] = 'HHE'

    hdr_hhn = hdr.copy()
    hdr_hhn['channel'] = 'HHN'

    stats_hhz = Stats(hdr_hhz)
    stats_hhe = Stats(hdr_hhe)
    stats_hhn = Stats(hdr_hhn)

    trace_hhz = Trace(data=data[:, 1], header=stats_hhz)
    trace_hhn = Trace(data=data[:, 2], header=stats_hhn)
    trace_hhe = Trace(data=data[:, 3], header=stats_hhe)
    stream = Stream([trace_hhz, trace_hhn, trace_hhe])
    return stream
