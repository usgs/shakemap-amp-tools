#!/usr/bin/env python

# stdlib imports
import os.path

# third party imports
import numpy as np

# local imports
from amptools.io.geonet.core import read_geonet
from pgm.pga import PGA


def test_pga():
    homedir = os.path.dirname(os.path.abspath(
        __file__))  # where is this script?
    datafile_v2 = os.path.join(homedir, '..', 'data', 'geonet',
                               '20161113_110259_WTMC_20.V2A')
    stream_v2 = read_geonet(datafile_v2)
    pga_obj = PGA()
    pga_dict = pga_obj.getPGM(stream_v2)
    np.testing.assert_almost_equal(pga_dict['HHE'], 81.28979591836733)
    np.testing.assert_almost_equal(pga_dict['HHN'], 99.3173469387755)
    np.testing.assert_almost_equal(pga_dict['HHZ'], 183.89693877551022)


if __name__ == '__main__':
    test_pga()
