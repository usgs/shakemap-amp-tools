#!/usr/bin/env python

# stdlib imports
import os.path

# third party imports
from obspy.core.stream import read
from obspy.core.utcdatetime import UTCDateTime
from amptools.process import check_max_amplitude, trim_to_window

def test_amp_check_trim():
    homedir = os.path.dirname(os.path.abspath(__file__))
    
    # read the two sac files for testing
    # one is unedited with a standard maximum amplitude
    # the second has been multiplied so that it fails the ampltidue check
    NOWS_tr = read(os.path.join(homedir, '..', 'data', 'process', 'NOWSENR.sac'))
    NOWS_tr_mul  = read(os.path.join(homedir, '..', 'data', 'process', 'NOWSENR_mul.sac'))
    
    assert check_max_amplitude(NOWS_tr) == True
    assert check_max_amplitude(NOWS_tr_mul) == False
    
    # Check that our trim and window function doesn't affect the ending time
    # of this record
    org_time = UTCDateTime('2001-02-14T22:03:58')
    assert NOWS_tr[0].stats.endtime == trim_to_window(NOWS_tr, org_time, 32.7195)[0].stats.endtime

if __name__ == '__main__':
    test_amp_check_trim()
    