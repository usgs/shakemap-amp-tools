#!/usr/bin/env python

import tempfile
import glob
import os.path
import numpy as np
from amptools.io.cwb.core import read_cwb
from amptools.io.geonet.core import read_geonet
from amptools.stream import streams_to_dataframe, GAL_TO_PCTG

def test_spectral():
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    datafile_v1 = os.path.join(homedir,'..','data','geonet','20161113_110259_WTMC_20.V1A')
    datafile_v2 = os.path.join(homedir,'..','data','geonet','20161113_110259_WTMC_20.V2A')
    stream_v1 = read_geonet(datafile_v1)
    stream_v2 = read_geonet(datafile_v2)
    df2,sp = streams_to_dataframe([stream_v2])

    assert df2['HHN']['psa03'].iloc[0]/323.8532 >= 0.95
    assert df2['HHN']['psa10'].iloc[0]/136.6972 >= 0.95
    assert df2['HHN']['psa30'].iloc[0]/17.9511 >= 0.95
    
    # Lat, Lon, Station, Channel, Accmax(%g), Velmax(cm/s), psa03 (%g), psa10 (%g), psa30 (%g),Abs pgamax (%g)
    # -42.619,173.054, WTMC, N28W,-112.3823,-101.655,323.8532,136.6972,17.9511,112.3823

def test():
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    datadir = os.path.join(homedir,'..','data','cwb')
    datafiles = glob.glob(os.path.join(datadir,'*.dat'))
    streams = []
    for datafile in datafiles:
        stream = read_cwb(datafile)
        streams.append(stream)
    df,sp = streams_to_dataframe(streams)
    pgasum = df['HHE']['pga'].sum()
    np.testing.assert_almost_equal(pgasum,1.7209452756509136)
    
    
if __name__ == '__main__':
    test_spectral()
    test()
