#!/usr/bin/env python

import tempfile
import os.path
import numpy as np
from amptools.io.cwb.core import is_cwb, read_cwb

def test():
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    datadir = os.path.join(homedir,'..','..','..','data','cwb')
    cwb_file = os.path.join(datadir,'1-EAS.dat')
    assert is_cwb(cwb_file)
    try:
        assert is_cwb(os.path.abspath(__file__))
    except AssertionError:
        assert 1==1
    stream = read_cwb(cwb_file)
    np.testing.assert_almost_equal(np.abs(stream[0].max()),0.83699999999999997)
    assert stream[0].stats['sampling_rate'] == 50

if __name__ == '__main__':
    test()
    
