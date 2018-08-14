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
from amptools.io.read import read_data
from amptools.stream import group_channels, streams_to_dataframe


def test_spectral():
    # where is this script?
    homedir = os.path.dirname(os.path.abspath(__file__))
    datafile_v2 = os.path.join(homedir, '..', 'data', 'geonet',
                               '20161113_110259_WTMC_20.V2A')
    stream_v2 = read_geonet(datafile_v2)
    df2, _ = streams_to_dataframe([stream_v2])

    assert df2['HN1']['SA(0.3)'].iloc[0]/323.8532 >= 0.95
    assert df2['HN1']['SA(1.0)'].iloc[0]/136.6972 >= 0.95
    assert df2['HN1']['SA(3.0)'].iloc[0]/17.9511 >= 0.95

    # Lat, Lon, Station, Channel, Accmax(%g), Velmax(cm/s), psa03 (%g), psa10 (%g), psa30 (%g),Abs pgamax (%g)
    # -42.619,173.054, WTMC, N28W,-112.3823,-101.655,323.8532,136.6972,17.9511,112.3823


def test():
    homedir = os.path.dirname(os.path.abspath(
        __file__))  # where is this script?
    datadir = os.path.join(homedir, '..', 'data', 'cwb')
    datafiles = glob.glob(os.path.join(datadir, '*.dat'))
    streams = []
    for datafile in datafiles:
        stream = read_cwb(datafile)
        streams.append(stream)
    df, _ = streams_to_dataframe(streams)
    pgasum = df['BN2']['PGA'].sum()
    np.testing.assert_almost_equal(pgasum, 1.7209452756509136, decimal=1)

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

def test_grouping():
    homedir = os.path.dirname(os.path.abspath(__file__))

    # cwb
    cwb_files = os.path.join(homedir, '..', 'data', 'cwb', '*')
    cwb_streams = []
    for filename in glob.glob(cwb_files):
        cwb_streams += [read_data(filename)]
    cwb_streams = group_channels(cwb_streams)
    assert len(cwb_streams) == 5
    for stream in cwb_streams:
        assert len(stream) == 3

    # dmg
    dmg_files = os.path.join(homedir, '..', 'data', 'dmg', '*.V2')
    dmg_streams = []
    for filename in glob.glob(dmg_files):
        if (not os.path.basename(filename).startswith('Bad') and
                not os.path.basename(filename).startswith('CE58667')):
            dmg_streams += [read_data(filename)]
    dmg_streams = group_channels(dmg_streams)
    assert len(dmg_streams) == 2
    for stream in dmg_streams:
        assert len(stream) == 3

    # geonet
    geonet_files = os.path.join(homedir, '..', 'data', 'geonet', '*')
    geonet_streams = []
    for filename in glob.glob(geonet_files):
        geonet_streams += [read_data(filename)]
    geonet_streams = group_channels(geonet_streams)
    assert len(geonet_streams) == 7
    for stream in geonet_streams:
        assert len(stream) == 3
        assert len(stream.select(station=stream[0].stats.station)) == 3
        level = stream[0].stats.standard.process_level
        for trace in stream:
            assert trace.stats.standard.process_level == level

    # kiknet
    kiknet_files = os.path.join(homedir, '..', 'data', 'kiknet', '*')
    kiknet_streams = []
    for filename in glob.glob(kiknet_files):
        kiknet_streams += [read_data(filename)]
    kiknet_streams = group_channels(kiknet_streams)
    assert len(kiknet_streams) == 1
    for stream in kiknet_streams:
        assert len(stream) == 3
        assert len(stream.select(station=stream[0].stats.station)) == 3

    # knet
    knet_files = os.path.join(homedir, '..', 'data', 'knet', '*')
    knet_streams = []
    for filename in glob.glob(knet_files):
        knet_streams += [read_data(filename)]
    knet_streams = group_channels(knet_streams)
    assert len(knet_streams) == 9
    for stream in knet_streams:
        assert len(stream) == 3
        assert len(stream.select(station=stream[0].stats.station)) == 3
        pl = stream[0].stats.standard.process_level
        for trace in stream:
            assert trace.stats.standard.process_level == pl

    # obspy
    obspy_files = os.path.join(homedir, '..', 'data', 'obspy', '*')
    obspy_streams = []
    for filename in glob.glob(obspy_files):
        if not filename.endswith('.json'):
            obspy_streams += [read_data(filename)]
    obspy_streams = group_channels(obspy_streams)
    assert len(obspy_streams) == 1
    for stream in obspy_streams:
        assert len(stream) == 3
        assert len(stream.select(station=stream[0].stats.station)) == 3

    # smc
    smc_files = os.path.join(homedir, '..', 'data', 'smc', '*')
    smc_streams = []
    for filename in glob.glob(smc_files):
        if not filename.endswith('.json'):
            smc_streams += [read_data(filename, any_structure=True)]
    smc_streams = group_channels(smc_streams)
    assert len(smc_streams) == 6
    for stream in smc_streams:
        if stream[0].stats.station == 'DVD0':
            assert len(stream) == 1
            assert len(stream.select(station=stream[0].stats.station)) == 1
        elif stream[0].stats.location == '01':
            assert len(stream) == 2
            assert len(stream.select(station=stream[0].stats.station)) == 2
        else:
            assert len(stream) == 3
            assert len(stream.select(station=stream[0].stats.station)) == 3

    # usc
    usc_files = os.path.join(homedir, '..', 'data', 'usc', '*')
    usc_streams = []
    for filename in glob.glob(usc_files):
        if not filename.endswith('.json'):
            if os.path.basename(filename) != '017m30bt.s0a':
                usc_streams += [read_data(filename)]
    usc_streams = group_channels(usc_streams)
    assert len(usc_streams) == 3
    for stream in usc_streams:
        if stream[0].stats.station == '57':
            assert len(stream) == 1
        else:
            assert len(stream) == 3


if __name__ == '__main__':
    test_spectral()
    test_grouping()
    test()
