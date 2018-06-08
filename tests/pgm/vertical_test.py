#!/usr/bin/env python

# stdlib imports
import os.path

# third party imports
import numpy as np

# local imports
from amptools.io.geonet.core import read_geonet
from pgm.station_summary import StationSummary


def test_vertical():
    homedir = os.path.dirname(os.path.abspath(
        __file__))  # where is this script?
    datafile_v2 = os.path.join(homedir, '..', 'data', 'geonet',
                               '20161113_110259_WTMC_20.V2A')
    stream_v2 = read_geonet(datafile_v2)
    station_summary = StationSummary(stream_v2,
            ['vertical'], ['pga'])
    station_dict = station_summary.pgms['PGA']
    vertical = station_dict['VERTICAL']
    np.testing.assert_almost_equal(vertical, 183.89693877551022)


if __name__ == '__main__':
    test_vertical()
