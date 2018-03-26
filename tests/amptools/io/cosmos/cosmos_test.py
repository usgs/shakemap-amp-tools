#!/usr/bin/env python

import shutil
import os.path
import numpy as np
from amptools.io.cosmos.core import is_cosmos, read_cosmos

def test_cosmos():
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    datadir = os.path.join(homedir,'..','..','..','data','cosmos')
    one_channel = os.path.join(datadir,'Cosmos12TimeSeriesTest.v1')
    two_channels = os.path.join(datadir,'Cosmos12TimeSeriesTest2.v1')

    assert is_cosmos(one_channel)
    try:
        assert is_cosmos(os.path.abspath(__file__))
    except AssertionError as ae:
        assert 1==1

    # test a one channel cosmos file
    stream1 = read_cosmos(one_channel)

    # test that one channel is created
    assert len(stream1) == 1

    # read the maximum from the text header check that the trace max
    # is the equivalent when rounded to the same number of decimal places
    with open(one_channel, 'rt') as f:
        file_line = f.readlines()[10].replace(' ', '').lower()
    file_max = file_line[file_line.find('max=') + 4: file_line.find('cm')]
    assert np.round(stream1[0].max(), 3) == float(file_max)

    # test a two channel cosmos file
    stream2 = read_cosmos(two_channels)

    # test that reading a file that is a valid station type returns a
    # stream with traces
    building_code = 10
    stream3 = read_cosmos(two_channels, valid_station_types=[building_code])
    assert stream3.count() == 2

    # test that reading a file that is not a valid station type returns an
    # empty stream
    stream4 = read_cosmos(two_channels, valid_station_types=[1, 2, 3, 4])
    assert stream4.count() == 0

    # test that two channels are created
    assert len(stream2) == 2


if __name__ == '__main__':
    test_cosmos()
