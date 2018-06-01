#!/usr/bin/env python

# stdlib imports
import os.path

# third party imports
import numpy as np

# local imports
from amptools.io.geonet.core import read_geonet
from pgm.imt.pga import PGA
from pgm.imc.greater_of_two_horizontals import GREATER_OF_TWO_HORIZONTALS


def test_greater_of_two_horizontals():
    homedir = os.path.dirname(os.path.abspath(
        __file__))  # where is this script?
    datafile_v2 = os.path.join(homedir, '..', 'data', 'geonet',
                               '20161113_110259_WTMC_20.V2A')
    stream_v2 = read_geonet(datafile_v2)
    pga_obj = PGA()
    pga_dict, pga_stream = pga_obj.getPGM(stream_v2)
    greater_of_two_obj = GREATER_OF_TWO_HORIZONTALS()
    greater_of_two_value, greater_of_two_stream = greater_of_two_obj.getPGM(pga_stream)
    np.testing.assert_almost_equal(greater_of_two_value, 99.3173469387755)


if __name__ == '__main__':
    test_greater_of_two_horizontals()
