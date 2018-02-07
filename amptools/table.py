# stdlib imports
import re
import os.path
import time

# third party imports
import pandas as pd
import numpy as np
from lxml import etree
from openpyxl import load_workbook


required_columns = ['station','latitude','longitude','network']
channel_groups = [['[a-z]{2}e','[a-z]{2}n','[a-z]{2}z'],
                  ['h1','h2','z'],
                  ['unk']]
pgm_cols = ['pga','pgv','psa03','psa10','psa30']
optional = ['location','distance','reference','intensity','source']

EXCEL_DESC = '''

'''

def read_excel(excelfile):
    """Read strong motion Excel spreadsheet, return a DataFrame.
    
    Args:
        excelfile (str): Path to valid Excel file.
    Returns:
        DataFrame: Multi-indexed dataframe as described below.
        str or None: Reference string or None.
        
     - "station" String containing UNIQUE identifying station information.
     - "latitude" Latitude where peak ground motion observations were made.
     - "longitude" Longitude where peak ground motion observations were made.
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

    # figure out if there is a little reference section in this...
    reference = None
    first_cell = 'A2'
    skip_rows = None
    header = [0,1]
    if ws['A1'].value.lower() == 'reference':
        reference = ws['B1'].value
        first_cell = 'A3'
        skip_rows = [0]
        header = [1,2]
    
    is_multi = True
    # if the first column of the second row is not empty,
    # then we do not have a multi-index.
    if ws[first_cell].value is not None:
        is_multi = False
    
    # read in dataframe, assuming that ground motions are grouped by channel
    if is_multi:
        try:
            df = pd.read_excel(excelfile,header=header)
        except pd.errors.ParserError as pe:
            raise IndexError('Input file has invalid empty first data row.')
        
        headers = df.columns.get_level_values(0).str.lower()
        subheaders = df.columns.get_level_values(1).str.lower()
        df.columns = pd.MultiIndex.from_arrays([headers,subheaders])
        top_headers = df.columns.levels[0]
    else:
        df = pd.read_excel(excelfile,skiprows=skip_rows)
        top_headers = df.columns
    
    # make sure basic columns are present
    if 'station' not in top_headers:
        df['station'] = df.index
        top_headers = df.columns.levels[0]
    if not set(required_columns).issubset(set(top_headers)):
        fmt = 'Input Excel file must specify the following columns: %s.'
        tpl = (str(required_columns))
        raise KeyError(fmt % tpl)
    

    # check if channel headers are valid
    channels = (set(top_headers) - set(required_columns)) - set(optional)
    valid = False
    if len(channels):
        for channel_group in channel_groups:
            num_channels = 0
            for channel_pat in channel_group:
                cp = re.compile(channel_pat)
                if len(list(filter(cp.match,channels))):
                    num_channels += 1
            if num_channels == 1 and len(channels) == 1:
                valid = True
                break
            elif num_channels > 1:
                h1_pat = re.compile(channel_group[0])
                h2_pat = re.compile(channel_group[1])
                has_h1 = len(list(filter(h1_pat.match,channels))) > 0
                has_h2 = len(list(filter(h2_pat.match,channels))) > 0
                if has_h1 or has_h2:
                    valid = True
                    break
    else:
        valid = True
    if not valid:
        raise KeyError('%s is not a valid channel grouping' % str(sorted(list(channels))))

    # make sure the empty cells are all nans or floats
    found = False
    if 'intensity' in top_headers:
        found = True
    empty_cell = re.compile('\s+')
    for channel in channels:
        channel_df = df[channel].copy()
        for column in pgm_cols:
            if column in channel_df:
                found = True
                channel_df[column] = channel_df[column].replace(empty_cell,np.nan)
                channel_df[column] = channel_df[column].astype(float)
        df[channel] = channel_df
    
    if not found:
        fmt = 'File must contain at least one of the following data columns: %s'
        tpl = (str(pgm_cols+['intensity']))
        raise KeyError(fmt % tpl)

    return (df,reference)

def dataframe_to_xml(df,eventid,dir,reference=None):
    """Write a dataframe to ShakeMap XML format.
    
    Args:
        df (DataFrame): Pandas dataframe, as described in read_excel.
        eventid (str): Event ID string.
        dir (str): Path to directory where XML file should be written.
    Returns:
        str: Path to output XML file.
    """
    top_headers = df.columns.levels[0]
    channels = (set(top_headers) - set(required_columns)) - set(optional)
    root = etree.Element('shakemap-data',code_version="3.5",map_version="3")

    create_time = int(time.time())
    stationlist = etree.SubElement(root,'stationlist',created='%i' % create_time)
    if reference is not None:
        stationlist.attrib['reference'] = reference
    
    for idx,row in df.iterrows():
        station = etree.SubElement(stationlist,'station')

        # assign required columns
        stationcode = row['station'].iloc[0].strip()
        netid = row['network'].iloc[0].strip()
        if not stationcode.startswith(netid):
            stationcode = '%s.%s' % (netid,stationcode)

        station.attrib['code'] = stationcode
        station.attrib['lat'] = '%.4f' % row['latitude'].iloc[0]
        station.attrib['lon'] = '%.4f' % row['longitude'].iloc[0]

        # assign optional columns
        if 'location' in top_headers:
            station.attrib['name'] = row['location'].iloc[0].strip()
        if 'network' in top_headers:
            station.attrib['netid'] = row['network'].iloc[0].strip()
        if 'distance' in top_headers:
            station.attrib['dist'] = '%.1f' % row['distance']
        if 'intensity' in top_headers:
            station.attrib['intensity'] = '%.1f' % row['intensity']
        if 'source' in top_headers:
            station.attrib['source'] = row['source'].iloc[0].strip()

        # sort channels by N,E,Z or H1,H2,Z
        channels = sorted(list(channels))
            
        for channel in channels:
            component = etree.SubElement(station,'comp')
            component.attrib['name'] = channel.upper()

            # create sub elements out of any of the PGMs
            for pgm in ['pga','pgv','psa03','psa10','psa30']:
                if pgm not in row[channel] or np.isnan(row[channel][pgm]):
                    continue
                if pgm in row[channel]:
                    pgm_el = etree.SubElement(component,pgm)
                    pgm_el.attrib['flag'] = '0'
                    pgm_el.attrib['value'] = '%.4f' % row[channel][pgm]

    
    outfile = os.path.join(dir,'%s_dat.xml' % eventid)
    tree = etree.ElementTree(root)
    tree.write(outfile,pretty_print=True)

    return outfile
