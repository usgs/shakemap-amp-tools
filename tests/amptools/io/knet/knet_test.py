#!/usr/bin/env python

import shutil
import tempfile
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
    except AssertionError as ae:
        assert 1==1

    # test a knet file with npoints % 10 == 0
    stream = read_knet(knet_file)

    # # test a file that has a number of points not divisible by 10
    # knet_file2 = os.path.join(datadir,'20161122_002004_NSPS_21.V1A')
    # stream2 = read_knet(knet_file2)

    # knet_file3 = os.path.join(datadir,'20161122_002021_NAAS_20.V1A')
    # stream3 = read_knet(knet_file3)
    
    # # test the values of these files
    
if __name__ == '__main__':
    test()
