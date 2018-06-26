# stdlib imports
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
    try:
        f = open(filename, 'rt')
        line = f.readline()
        f.close()
        if line.startswith('#Earthquake Information'):
            return True
    except UnicodeDecodeError:
        return False
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
    # according to the powers that defined the Network.Station.Channel.Location
    # "standard", Location is a two character field.  Most data providers,
    # including CWB here, don't provide this.  We'll flag it as "--".
    data = np.genfromtxt(filename, skip_header=HDR_ROWS,
                         delimiter=[COLWIDTH] * NCOLS)  # time, Z, NS, EW

    hdr = _get_header_info(f, data)
    f.close()

    hdr_hhz = hdr.copy()
    hdr_hhz['channel'] = 'HHZ'
    hdr_hhz['standard']['horizontal_orientation'] = np.nan

    hdr_hhe = hdr.copy()
    hdr_hhe['channel'] = 'HHE'
    hdr_hhz['standard']['horizontal_orientation'] = np.nan

    hdr_hhn = hdr.copy()
    hdr_hhn['channel'] = 'HHN'
    hdr_hhz['standard']['horizontal_orientation'] = np.nan

    stats_hhz = Stats(hdr_hhz)
    stats_hhe = Stats(hdr_hhe)
    stats_hhn = Stats(hdr_hhn)

    trace_hhz = Trace(data=data[:, 1], header=stats_hhz)
    trace_hhn = Trace(data=data[:, 2], header=stats_hhn)
    trace_hhe = Trace(data=data[:, 3], header=stats_hhe)
    stream = Stream([trace_hhz, trace_hhn, trace_hhe])
    return stream


def _get_header_info(file, data):
    """Return stats structure from various headers.

    Output is a dictionary like this:
     - network (str): Always CWB
     - station (str)
     - channel (str)
     - location (str): Default is '--'
     - starttime (datetime)
     - duration (float)
     - sampling_rate (float)
     - delta (float)
     - npts (int)
     - coordinates:
       - latitude (float)
       - longitude (float)
       - elevation (float): Default is np.nan
    - standard (Defaults are either np.nan or '')
      - horizontal_orientation (float): Rotation from north (degrees)
      - instrument_period (float): Period of sensor (Hz)
      - instrument_damping (float): Fraction of critical
      - process_time (datetime): Reported date of processing
      - process_level: Either 'V0', 'V1', 'V2', or 'V3'
      - station_name (str): Long form station description
      - sensor_serial_number (str): Reported sensor serial
      - instrument (str)
      - comments (str): Processing comments
      - structure_type (str)
      - corner_frequency (float): Sensor corner frequency (Hz)
      - units (str)
      - source (str): Network source description
      - source_format (str): Always cwb
    - format_specific
        - dc_offset_hhz (float)
        - dc_offset_hhe (float)
        - dc_offset_hhn (float)

    Args:
        file (TextIOWrapper): File object containing data
        data (ndarray): Array of strong motion data

    Returns:
        dictionary: Dictionary of header/metadata information
    """
    hdr = OrderedDict()
    coordinates = {}
    standard = {}
    format_specific = {}
    hdr['location'] = '--'
    while True:
        line = file.readline()
        if line.startswith('#StationCode'):
            hdr['station'] = line.split(':')[1].strip()
        if line.startswith('#StationName'):
            standard['station_name'] = line.split(':')[1].strip()
        if line.startswith('#StationLongitude'):
            coordinates['longitude'] = float(line.split(':')[1].strip())
        if line.startswith('#StationLatitude'):
            coordinates['latitude'] = float(line.split(':')[1].strip())
        if line.startswith('#StartTime'):
            timestr = ':'.join(line.split(':')[1:]).strip()
            hdr['starttime'] = datetime.strptime(timestr, DATE_FMT)
        if line.startswith('#RecordLength'):
            hdr['duration'] = float(line.split(':')[1].strip())
        if line.startswith('#SampleRate'):
            hdr['sampling_rate'] = int(line.split(':')[1].strip())
        if line.startswith('#InstrumentKind'):
            standard['instrument'] = line.split(':')[1].strip()
        if line.startswith('#AmplitudeMAX. U:'):
            format_specific['dc_offset_hhz'] = float(line.split('~')[1])
        if line.startswith('#AmplitudeMAX. N:'):
            format_specific['dc_offset_hhn'] = float(line.split('~')[1])
        if line.startswith('#AmplitudeMAX. E:'):
            format_specific['dc_offset_hhe'] = float(line.split('~')[1])
        if line.startswith('#Data'):
            break

    # correct start time to GMT
    hdr['starttime'] = hdr['starttime'] - timedelta(seconds=GMT_OFFSET)
    nrows, _ = data.shape
    # Add some optional information to the header
    hdr['network'] = 'CWB'
    hdr['delta'] = 1 / hdr['sampling_rate']
    hdr['calib'] = 1.0
    standard['units'] = 'acc'  # cm/s**2
    hdr['source'] = 'Taiwan Central Weather Bureau'
    hdr['npts'] = nrows
    secs = int(data[-1, 0])
    microsecs = int((data[-1, 0] - secs) * 1e6)
    hdr['endtime'] = hdr['starttime'] + \
        timedelta(seconds=secs, microseconds=microsecs)

    # Set defaults
    coordinates['elevation'] = np.nan
    if 'longitude' not in coordinates:
        coordinates['longitude'] = np.nan
    if 'latitude' not in coordinates:
        coordinates['latitude'] = np.nan
    standard['instrument_period'] = np.nan
    standard['instrument_damping'] = np.nan
    standard['process_time'] = np.nan
    standard['process_level'] = 'V1'
    standard['sensor_serial_number'] = ''
    standard['comments'] = ''
    standard['structure_type'] = ''
    standard['corner_frequency'] = np.nan
    standard['source'] = 'Taiwan Strong Motion Instrumentation Program' + \
        'via Central Weather Bureau'
    standard['source_format'] = 'cwb'
    if 'station_name' not in standard:
        standard['station_name'] = ''
    if 'instrument' not in standard:
        standard['instrument'] = ''
    if 'dc_offset_hhz' not in format_specific:
        format_specific['dc_offset_hhz'] = np.nan
    if 'dc_offset_hhe' not in format_specific:
        format_specific['dc_offset_hhe'] = np.nan
    if 'dc_offset_hhn' not in format_specific:
        format_specific['dc_offset_hhn'] = np.nan
    # Set dictionary
    hdr['standard'] = standard
    hdr['coordinates'] = coordinates
    hdr['format_specific'] = format_specific
    return hdr
