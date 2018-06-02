#!/usr/bin/env python

# stdlib imports
import os.path

# third party imports
import numpy as np

# local imports
from amptools.io.geonet.core import read_geonet
from pgm.imt.sa import SA


def test_sa():
    homedir = os.path.dirname(os.path.abspath(
        __file__))  # where is this script?
    datafile_v2 = os.path.join(homedir, '..', 'data', 'geonet',
                               '20161113_110259_WTMC_20.V2A')
    stream_v2 = read_geonet(datafile_v2)
    sa_target = {}
    for trace in stream_v2:
        vtrace = trace.copy()
        vtrace.integrate()
        sa_target[vtrace.stats['channel']] = np.abs(vtrace.max())
    sa_obj = SA()
    sa_dict, sa_stream = sa_obj.getPGM(stream_v2, period=2)
    assert sa_obj._units == '%%g'
    assert sa_obj.period == 2
    assert sa_obj.period_str == 'T2.00'


if __name__ == '__main__':
    test_sa()
