#!/usr/bin/env python

# stdlib imports
import warnings
import glob
import os.path

# third party imports
import numpy as np
from amptools.io.cwb.core import read_cwb
from amptools.io.geonet.core import read_geonet
from amptools.io.knet.core import read_knet
from amptools.stream import group_channels, streams_to_dataframe

def test_spectral():
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    datafile_v2 = os.path.join(homedir, '..', 'data', 'geonet',
            '20161113_110259_WTMC_20.V2A')
    stream_v2 = read_geonet(datafile_v2)
    df2,_ = streams_to_dataframe([stream_v2])

    assert df2['H1']['psa03'].iloc[0]/323.8532 >= 0.95
    assert df2['H1']['psa10'].iloc[0]/136.6972 >= 0.95
    assert df2['H1']['psa30'].iloc[0]/17.9511 >= 0.95

    # Lat, Lon, Station, Channel, Accmax(%g), Velmax(cm/s), psa03 (%g), psa10 (%g), psa30 (%g),Abs pgamax (%g)
    # -42.619,173.054, WTMC, N28W,-112.3823,-101.655,323.8532,136.6972,17.9511,112.3823

def test():
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    datadir = os.path.join(homedir, '..', 'data', 'cwb')
    datafiles = glob.glob(os.path.join(datadir, '*.dat'))
    streams = []
    for datafile in datafiles:
        stream = read_cwb(datafile)
        streams.append(stream)
    df,_ = streams_to_dataframe(streams)
    pgasum = df['HHE']['pga'].sum()
    np.testing.assert_almost_equal(pgasum, 1.7209452756509136)

    # Test for channel grouping with three unique channels
    streams = []
    datadir = os.path.join(homedir, '..', 'data', 'knet')
    for ext in ['.EW', '.NS', '.UD']:
        filename = 'AOM0031801241951' + ext
        datafile = os.path.join(homedir, '..', 'data', 'knet', filename)
        streams += [read_knet(datafile)]
    grouped_streams = group_channels(streams)
    assert len(grouped_streams) == 1
    assert grouped_streams[0].count() == 3

    # Test for channel grouping with three more duplicate channels
    for ext in ['.EW', '.NS', '.UD']:
        filename = 'AOM0031801241951' + ext
        datafile = os.path.join(homedir, '..', 'data', 'knet', filename)
        streams += [read_knet(datafile)]
    grouped_streams = group_channels(streams)
    assert len(grouped_streams) == 1
    assert grouped_streams[0].count() == 3

    # Test for channel grouping with more file types
    filename = '20161113_110313_THZ_20.V2A'
    datafile = os.path.join(homedir, '..', 'data', 'geonet', filename)
    streams += [read_geonet(datafile)]
    grouped_streams = group_channels(streams)
    assert len(grouped_streams) == 2
    assert grouped_streams[0].count() == 3
    assert grouped_streams[1].count() == 3

    # Test for warning for one channel streams
    filename = 'AOM0071801241951.UD'
    datafile = os.path.join(homedir, '..', 'data', 'knet', filename)
    streams += [read_knet(datafile)]
    with warnings.catch_warnings(record=True) as w:
        grouped_streams = group_channels(streams)
        assert issubclass(w[-1].category, Warning)
        assert "One channel stream:" in str(w[-1].message)
    assert len(grouped_streams) == 3
    assert grouped_streams[0].count() == 3
    assert grouped_streams[1].count() == 3
    assert grouped_streams[2].count() == 1

if __name__ == '__main__':
    test_spectral()
    test()
