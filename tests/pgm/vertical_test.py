#!/usr/bin/env python

# stdlib imports
import os.path

# third party imports
import numpy as np

# local imports
from amptools.io.geonet.core import read_geonet
from pgm.imt.pga import PGA
from pgm.imc.vertical import VERTICAL


def test_vertical():
    homedir = os.path.dirname(os.path.abspath(
        __file__))  # where is this script?
    datafile_v2 = os.path.join(homedir, '..', 'data', 'geonet',
                               '20161113_110259_WTMC_20.V2A')
    stream_v2 = read_geonet(datafile_v2)
    pga_obj = PGA()
    pga_dict, pga_stream = pga_obj.getPGM(stream_v2)
    vertical_obj = VERTICAL()
    vertical_value, vertical_stream = vertical_obj.getPGM(pga_stream)
    np.testing.assert_almost_equal(vertical_value, 183.89693877551022)


if __name__ == '__main__':
    test_vertical()
