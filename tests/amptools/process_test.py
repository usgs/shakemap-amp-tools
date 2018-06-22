#!/usr/bin/env python

# stdlib imports
import os.path
import numpy as np

# third party imports
from obspy.core.stream import read
from obspy.core.utcdatetime import UTCDateTime
from amptools.process import check_max_amplitude, trim_total_window, get_corner_frequencies
from amptools.process import zero_pad, taper_total_waveform

# function that will test check_max_ammplitude and trim
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
    assert NOWS_tr[0].stats.endtime == trim_total_window(NOWS_tr, org_time, 32.7195)[0].stats.endtime
    
def test_taper_pad():
    homedir = os.path.dirname(os.path.abspath(__file__))
    ALCT_tr = read(os.path.join(homedir, '..', 'data', 'process', 'ALCTENE.UW..sac'))[0]
    ALCT_padded = zero_pad(ALCT_tr)
    assert ALCT_padded.stats.npts == 16384
    
    ALCT_tapered = taper_total_waveform(ALCT_tr)
    np.testing.assert_allclose(ALCT_tapered.data[0], 0.0, atol=0.001)

def test_corner_freqs():
    homedir = os.path.dirname(os.path.abspath(__file__))
    event_time = UTCDateTime('2001-02-28T18:54:32')
    
    ALCT_tr = read(os.path.join(homedir, '..', 'data', 'process', 'ALCTENE.UW..sac'))[0]
    ALCT_dist = 75.9559
    
    GNW_tr = read(os.path.join(homedir, '..', 'data', 'process', 'GNWBHE.UW..sac'))[0]
    GNW_dist = 46.7473
    
    np.testing.assert_allclose(get_corner_frequencies(ALCT_tr, event_time, ALCT_dist), [0.03662, 50.0], atol=0.001)
    np.testing.assert_allclose(get_corner_frequencies(GNW_tr, event_time, GNW_dist), [0.03662, 25.0], atol=0.001)
    
    event_time = UTCDateTime('2016-10-22T17:17:05')
    ALKI_tr = read(os.path.join(homedir, '..', 'data', 'process', 'ALKIENE.UW..sac'))[0]
    ALKI_dist = 37.87883
    
    np.testing.assert_allclose(get_corner_frequencies(ALKI_tr, event_time, ALKI_dist), [-1, -1], atol=0)

if __name__ == '__main__':
    test_amp_check_trim()
    test_taper_pad()
    test_corner_freqs()
    