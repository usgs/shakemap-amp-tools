#!/usr/bin/env python

# stdlib imports
import os.path

# third party imports
import numpy as np

# local imports
from amptools.io.geonet.core import read_geonet
from pgm.imt.pgv import PGV


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
    pgv_obj = PGV()
    pgv_dict, pgv_stream = pgv_obj.getPGM(stream_v2)
    np.testing.assert_almost_equal(pgv_dict['HHE'], pgv_target['HHE'])
    np.testing.assert_almost_equal(pgv_dict['HHN'], pgv_target['HHN'])
    np.testing.assert_almost_equal(pgv_dict['HHZ'], pgv_target['HHZ'])


if __name__ == '__main__':
    test_pgv()
