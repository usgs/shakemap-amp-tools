# stdlib imports
import re
import os.path
import time
import string

# third party imports
import pandas as pd
import numpy as np
from lxml import etree
from openpyxl import load_workbook, utils


REQUIRED_COLUMNS = ['station', 'lat', 'lon', 'network']
CHANNEL_GROUPS = [['[a-z]{2}e', '[a-z]{2}n', '[a-z]{2}z'],
                  ['h1', 'h2', 'z'],
                  ['unk']]
PGM_COLS = ['pga', 'pgv', 'psa03', 'psa10', 'psa30']
OPTIONAL = ['location', 'distance', 'reference', 'intensity', 'source']


def _move(cellstr, nrows, ncols):
    """Internal method for getting new cell coordinate by adding rows/columns to cell coordinate.

    'A1' moved by 1 row, 1 column => 'B2'

    Args:
        cellstr (str): Cell coordinate (A1,B2)
        nrows (int): Number of rows to move (usually down)
        ncols (int): Number of columns to move (usually right)
    Returns:
        str: New cell coordinate.
    """
    # WARNING! This will only work up to column Z!
    # colidx is a string, rowidx is a number
    col_str_idx, rowidx = utils.coordinate_from_string(cellstr)
    letters = string.ascii_uppercase
    try:
        colidx = letters.index(col_str_idx)
        newcolidx = colidx + ncols
        newrowidx = rowidx + nrows
        newcellstr = '%s%i' % (letters[newcolidx], newrowidx)
        return newcellstr
    except ValueError as ve:
        raise ValueError('Could not add %i columns to column %s.' %
                         (ncols, col_str_idx))


def read_excel(excelfile):
    """Read strong motion Excel spreadsheet, return a DataFrame.

    Args:
        excelfile (str): Path to valid Excel file.
    Returns:
        DataFrame: Multi-indexed dataframe as described below.
        str or None: Reference string or None.

     - "station" String containing UNIQUE identifying station information.
     - "lat" Latitude where peak ground motion observations were made.
     - "lon" Longitude where peak ground motion observations were made.
     - "network" (usually) two letter code indicating the source network.

    Optional columns include:
     - "location" String describing area where peak ground motions were observed.
     - "source" String describing (usu. long form) source of peak ground motion data.
     - "network" String describing network (us,ci,nc, etc.).
     - "distance" Distance from epicenter to station location, in units of km.

    And then at least one of the following columns:
     - "intensity" MMI value (1-10).

        AND/OR 
      a grouped set of per-channel peak ground motion columns, like this:

      -------------------------------------------------------------------------------
      |         H1              |           H2            |             Z           |
      -------------------------------------------------------------------------------
      |pga|pgv|psa03|psa10|psa30|pga|pgv|psa03|psa10|psa30|pga|pgv|psa03|psa10|psa30|
      -------------------------------------------------------------------------------

      The peak ground motion columns can be any of the following:
      - "pga" Peak ground acceleration in units of %g.
      - "pgv" Peak ground velocity in units of cm/sec.
      - "psa03" Peak spectral acceleration at 0.3 seconds, in units of %g.
      - "psa10" Peak spectral acceleration at 1.0 seconds, in units of %g.
      - "psa30" Peak spectral acceleration at 3.0 seconds, in units of %g.

    Valid "channel" columns are {H1,H2,Z} or {XXN,XXE,XXZ}, where 'XX' is any
    two-letter combination, usually adhering to the following standard:
    http://www.fdsn.org/seed_manual/SEEDManual_V2.4_Appendix-A.pdf

    If the input data set provides no channel information, then the channel can be simply
    "UNK".

    """

    # figure out if data frame is multi-index or not
    wb = load_workbook(excelfile)
    ws = wb.active

    # figure out where the top left of the data begins
    topleft = 'A1'
    first_cell = 'A2'
    second_cell = 'A3'

    # figure out if there is a little reference section in this...
    reference = None
    skip_rows = None
    header = [0, 1]
    if ws[topleft].value.lower() != 'reference':
        raise KeyError('Reference cells are required in A1 and B1!')
    refcell = _move(topleft, 0, 1)
    reference = ws[refcell].value
    first_cell = _move(topleft, 1, 0)
    second_cell = _move(first_cell, 1, 0)
    skip_rows = [0]
    header = [1, 2]

    is_multi = True
    # if the first column of the second row is not empty,
    # then we do not have a multi-index.
    if ws[second_cell].value is not None:
        is_multi = False

    # read in dataframe, assuming that ground motions are grouped by channel
    if is_multi:
        try:
            df = pd.read_excel(excelfile, header=header)
        except pd.errors.ParserError as pe:
            raise IndexError('Input file has invalid empty first data row.')

        headers = df.columns.get_level_values(0).str.lower()
        subheaders = df.columns.get_level_values(1).str.lower()
        df.columns = pd.MultiIndex.from_arrays([headers, subheaders])
        top_headers = df.columns.levels[0]
    else:
        df = pd.read_excel(excelfile, skiprows=skip_rows)
        top_headers = df.columns

    # make sure basic columns are present
    if 'station' not in top_headers:
        df['station'] = df.index
        top_headers = df.columns.levels[0]
    if not set(REQUIRED_COLUMNS).issubset(set(top_headers)):
        fmt = 'Input Excel file must specify the following columns: %s.'
        tpl = (str(REQUIRED_COLUMNS))
        raise KeyError(fmt % tpl)

    # check if channel headers are valid
    channels = (set(top_headers) - set(REQUIRED_COLUMNS)) - set(OPTIONAL)
    valid = False
    if len(channels):
        for channel_group in CHANNEL_GROUPS:
            num_channels = 0
            for channel_pat in channel_group:
                cp = re.compile(channel_pat)
                if len(list(filter(cp.match, channels))):
                    num_channels += 1
            if num_channels == 1 and len(channels) == 1:
                valid = True
                break
            elif num_channels > 1:
                h1_pat = re.compile(channel_group[0])
                h2_pat = re.compile(channel_group[1])
                has_h1 = len(list(filter(h1_pat.match, channels))) > 0
                has_h2 = len(list(filter(h2_pat.match, channels))) > 0
                if has_h1 or has_h2:
                    valid = True
                    break
    else:
        valid = True
    if not valid:
        raise KeyError('%s is not a valid channel grouping' %
                       str(sorted(list(channels))))

    # make sure the empty cells are all nans or floats
    found = False
    if 'intensity' in top_headers:
        found = True
    empty_cell = re.compile('\s+')
    for channel in channels:
        channel_df = df[channel].copy()
        for column in PGM_COLS:
            if column in channel_df:
                found = True
                channel_df[column] = channel_df[column].replace(
                    empty_cell, np.nan)
                channel_df[column] = channel_df[column].astype(float)
        df[channel] = channel_df

    if not found:
        fmt = 'File must contain at least one of the following data columns: %s'
        tpl = (str(PGM_COLS + ['intensity']))
        raise KeyError(fmt % tpl)

    return (df, reference)


def dataframe_to_xml(df, eventid, dir, reference=None):
    """Write a dataframe to ShakeMap XML format.

    Args:
        df (DataFrame): Pandas dataframe, as described in read_excel.
        eventid (str): Event ID string.
        dir (str): Path to directory where XML file should be written.
    Returns:
        str: Path to output XML file.
    """
    if hasattr(df.columns, 'levels'):
        top_headers = df.columns.levels[0]
        channels = (set(top_headers) - set(REQUIRED_COLUMNS)) - set(OPTIONAL)
    else:
        channels = []
    root = etree.Element('shakemap-data', code_version="3.5", map_version="3")

    create_time = int(time.time())
    stationlist = etree.SubElement(
        root, 'stationlist', created='%i' % create_time)
    if reference is not None:
        stationlist.attrib['reference'] = reference

    for idx, row in df.iterrows():
        station = etree.SubElement(stationlist, 'station')

        tmprow = row.copy()
        if isinstance(tmprow.index, pd.core.indexes.multi.MultiIndex):
            tmprow.index = tmprow.index.droplevel(1)

        # assign required columns
        stationcode = tmprow['station'].strip()
        netid = tmprow['network'].strip()
        if not stationcode.startswith(netid):
            stationcode = '%s.%s' % (netid, stationcode)

        station.attrib['code'] = stationcode
        station.attrib['lat'] = '%.4f' % tmprow['lat']
        station.attrib['lon'] = '%.4f' % tmprow['lon']

        # assign optional columns
        if 'location' in tmprow:
            station.attrib['name'] = tmprow['location'].strip()
        if 'network' in tmprow:
            station.attrib['netid'] = tmprow['network'].strip()
        if 'distance' in tmprow:
            station.attrib['dist'] = '%.1f' % tmprow['distance']
        if 'intensity' in tmprow:
            station.attrib['intensity'] = '%.1f' % tmprow['intensity']
        if 'source' in tmprow:
            station.attrib['source'] = tmprow['source'].strip()

        # sort channels by N,E,Z or H1,H2,Z
        channels = sorted(list(channels))

        for channel in channels:
            component = etree.SubElement(station, 'comp')
            component.attrib['name'] = channel.upper()

            # create sub elements out of any of the PGMs
            for pgm in ['pga', 'pgv', 'psa03', 'psa10', 'psa30']:
                if pgm not in row[channel] or np.isnan(row[channel][pgm]):
                    continue
                if pgm in row[channel]:
                    pgm_el = etree.SubElement(component, pgm)
                    pgm_el.attrib['flag'] = '0'
                    pgm_el.attrib['value'] = '%.4f' % row[channel][pgm]

    outfile = os.path.join(dir, '%s_dat.xml' % eventid)
    tree = etree.ElementTree(root)
    tree.write(outfile, pretty_print=True)

    return outfile
