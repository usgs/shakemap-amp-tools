#!/usr/bin/env python

import os.path
import numpy as np
from amptools.io.knet.core import is_knet, read_knet

def test():
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    datadir = os.path.join(homedir,'..','..','..','data','knet')
    knet_file = os.path.join(datadir,'AOM0051801241951.EW')
    assert is_knet(knet_file)
    try:
        assert is_knet(os.path.abspath(__file__))
    except AssertionError:
        assert 1==1

    # test a knet file with npoints % 10 == 0
    stream = read_knet(knet_file)
    np.testing.assert_almost_equal(stream[0].max(),29.070,decimal=2)
    np.testing.assert_almost_equal(stream[1].max(),28.821,decimal=2)
    np.testing.assert_almost_equal(stream[2].max(),11.817,decimal=2)

    # test a file that has a number of points divisible by 8
    knet_file2 = os.path.join(datadir,'AOM0011801241951.EW')
    stream2 = read_knet(knet_file2)
    np.testing.assert_almost_equal(stream2[0].max(),4.078,decimal=2)
    np.testing.assert_almost_equal(stream2[1].max(),-4.954,decimal=2)
    np.testing.assert_almost_equal(stream2[2].max(),-2.240,decimal=2)
    
if __name__ == '__main__':
    test()
