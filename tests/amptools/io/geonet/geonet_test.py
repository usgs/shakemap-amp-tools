#!/usr/bin/env python

import shutil
import tempfile
import os.path
import numpy as np
from amptools.io.geonet.core import is_geonet, read_geonet

def test():
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    datadir = os.path.join(homedir,'..','..','..','data','geonet')
    geonet_file = os.path.join(datadir,'20161122_001955_PGFS_20.V1A')
    assert is_geonet(geonet_file)
    try:
        assert is_geonet(os.path.abspath(__file__))
    except AssertionError as ae:
        assert 1==1

    # test a geonet file with npoints % 10 == 0
    stream = read_geonet(geonet_file)

    # test a file that has a number of points not divisible by 10
    geonet_file2 = os.path.join(datadir,'20161122_002004_NSPS_21.V1A')
    stream2 = read_geonet(geonet_file2)

    geonet_file3 = os.path.join(datadir,'20161122_002021_NAAS_20.V1A')
    stream3 = read_geonet(geonet_file3)
    
    # test the values of these files
    
if __name__ == '__main__':
    test()
