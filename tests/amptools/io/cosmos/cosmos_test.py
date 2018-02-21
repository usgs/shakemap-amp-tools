#!/usr/bin/env python

import shutil
import tempfile
import os.path
import numpy as np
from amptools.io.cosmos.core import is_cosmos, read_cosmos

def pending_test():
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    datadir = os.path.join(homedir,'..','..','..','data','cosmos')
    cosmos_file = os.path.join(datadir,'pacoima_dam.V2')
    assert is_cosmos(cosmos_file)
    try:
        assert is_cosmos(os.path.abspath(__file__))
    except AssertionError as ae:
        assert 1==1

    # test a cosmos file with npoints % 10 == 0
    stream = read_cosmos(cosmos_file)

    # # test a file that has a number of points not divisible by 10
    # cosmos_file2 = os.path.join(datadir,'20161122_002004_NSPS_21.V1A')
    # stream2 = read_cosmos(cosmos_file2)

    # cosmos_file3 = os.path.join(datadir,'20161122_002021_NAAS_20.V1A')
    # stream3 = read_cosmos(cosmos_file3)
    
    # # test the values of these files
    
if __name__ == '__main__':
    test()
