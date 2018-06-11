#!/usr/bin/env python

# stdlib imports
import os.path

# third party imports
import numpy as np

# local imports
from amptools.io.geonet.core import read_geonet
from pgm.station_summary import StationSummary


def test_pgv():
    homedir = os.path.dirname(os.path.abspath(
        __file__))  # where is this script?
    datafile_v2 = os.path.join(homedir, '..', 'data', 'geonet',
                               '20161113_110259_WTMC_20.V2A')
    stream_v2 = read_geonet(datafile_v2)
    pgv_target = {}
    for trace in stream_v2:
        vtrace = trace.copy()
        vtrace.integrate()
        pgv_target[vtrace.stats['channel']] = np.abs(vtrace.max())
    station_summary = StationSummary(stream_v2,
            ['channels', 'greater_of_two_horizontals', 'gmrotd50'],
            ['pgv', 'sa1.0', 'saincorrect'])
    station_dict = station_summary.pgms['PGV']
    np.testing.assert_almost_equal(station_dict['HHE'], pgv_target['HHE'])
    np.testing.assert_almost_equal(station_dict['HHN'], pgv_target['HHN'])
    np.testing.assert_almost_equal(station_dict['HHZ'], pgv_target['HHZ'])


if __name__ == '__main__':
    test_pgv()
