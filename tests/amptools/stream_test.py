#!/usr/bin/env python

import shutil
import tempfile
import glob
import os.path
import numpy as np
from amptools.io.cwb.core import read_cwb
from amptools.stream import streams_to_dataframe

def test():
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    datadir = os.path.join(homedir,'..','data','cwb')
    datafiles = glob.glob(os.path.join(datadir,'*.dat'))
    streams = []
    for datafile in datafiles:
        stream = read_cwb(datafile)
        streams.append(stream)
    df = streams_to_dataframe(streams)
    
    
if __name__ == '__main__':
    test()
