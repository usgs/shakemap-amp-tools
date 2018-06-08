#!/usr/bin/env python

# stdlib imports
import os.path

# third party imports
import numpy as np

# local imports
from amptools.io.geonet.core import read_geonet
from pgm.station_summary import StationSummary


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
    station_summary = StationSummary(stream_v2,
            ['vertical', 'greater_of_two_horizontals', 'gmrotd50'],
            ['sa1.0', 'saincorrect'])
    #station_dict = station_summary.pgms['SA1.0']
    # TODO: test against real values


if __name__ == '__main__':
    test_sa()
