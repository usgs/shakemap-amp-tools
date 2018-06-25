#!/usr/bin/env python

# stdlib imports
import os.path
import numpy as np

# third party imports
from obspy.core.stream import read
from obspy.core.utcdatetime import UTCDateTime
from amptools import process


def test_amp_check_trim():
    homedir = os.path.dirname(os.path.abspath(__file__))

    # read the two sac files for testing
    # one is unedited with a standard maximum amplitude
    # the second has been multiplied so that it fails the ampltidue check
    NOWS_tr = read(os.path.join(homedir, '..', 'data', 'process',
                                'NOWSENR.sac'))[0]
    NOWS_tr_mul = read(os.path.join(homedir, '..', 'data', 'process',
                                    'NOWSENR_mul.sac'))[0]

    assert process.check_max_amplitude(NOWS_tr) == True
    assert process.check_max_amplitude(NOWS_tr_mul) == False

    # Check that our trim and window function doesn't affect the ending time
    # of this record
    org_time = UTCDateTime('2001-02-14T22:03:58')
    trim = process.trim_total_window(NOWS_tr, org_time, 32.7195).stats.endtime
    assert NOWS_tr.stats.endtime == trim


def test_corner_freqs():
    homedir = os.path.dirname(os.path.abspath(__file__))
    event_time = UTCDateTime('2001-02-28T18:54:32')

    ALCT_tr = read(os.path.join(homedir, '..', 'data', 'process',
                                'ALCTENE.UW..sac'))[0]
    ALCT_dist = 75.9559

    GNW_tr = read(os.path.join(homedir, '..', 'data', 'process',
                               'GNWBHE.UW..sac'))[0]
    GNW_dist = 46.7473

    corners_1 = process.get_corner_frequencies(ALCT_tr, event_time, ALCT_dist)
    np.testing.assert_allclose(corners_1, [0.03662, 50.0], atol=0.001)

    corners_2 = process.get_corner_frequencies(GNW_tr, event_time, GNW_dist)
    np.testing.assert_allclose(corners_2, [0.03662, 25.0], atol=0.001)

    event_time = UTCDateTime('2016-10-22T17:17:05')
    ALKI_tr = read(os.path.join(homedir, '..', 'data', 'process',
                                'ALKIENE.UW..sac'))[0]
    ALKI_dist = 37.87883

    corners_3 = process.get_corner_frequencies(ALKI_tr, event_time, ALKI_dist)
    np.testing.assert_allclose(corners_3, [-1, -1], atol=0)


def test_all():
    homedir = os.path.dirname(os.path.abspath(__file__))
    event_time = UTCDateTime('2001-02-28T18:54:32')
    ALCT_dist = 75.9559
    ALCT_tr = read(os.path.join(homedir, '..', 'data', 'process',
                                'ALCTENE.UW..sac'))[0]

    GNW_tr = read(os.path.join(homedir, '..', 'data', 'process',
                               'GNWBHE.UW..sac'))[0]
    GNW_dist = 46.7473
    GNW_processed = process.rennolet_process(GNW_tr, event_time, GNW_dist)
    last_point = GNW_processed.data[GNW_processed.stats.npts-1]
    np.testing.assert_allclose(last_point, 0, atol=0.0001)

    # Triggers the invalid low pass filtering message
    ALCT_processed = process.rennolet_process(ALCT_tr, event_time, ALCT_dist)
    last_point = ALCT_processed.data[ALCT_processed.stats.npts-1]
    np.testing.assert_allclose(last_point, 0, atol=0.0001)

    # Test trace with invalid amplitudes
    NOWS_tr_mul = read(os.path.join(homedir, '..', 'data', 'process',
                                    'NOWSENR_mul.sac'))[0]
    time = UTCDateTime('2001-02-14T22:03:58')
    dist = 50.05
    assert process.rennolet_process(NOWS_tr_mul, time, dist) == NOWS_tr_mul

    # Test trace with low S/N ratio
    event_time = UTCDateTime('2016-10-22T17:17:05')
    ALKI_tr = read(os.path.join(homedir, '..', 'data', 'process',
                                'ALKIENE.UW..sac'))[0]
    ALKI_dist = 37.87883
    ALKI_processed = process.rennolet_process(ALKI_tr, event_time, ALKI_dist)
    assert ALKI_processed == ALKI_tr

    # Test file that will conduct low-pass filter
    event_time = UTCDateTime('2001-02-28T18:54:32')
    BRI_dist = 55.6385
    BRI_tr = read(os.path.join(homedir, '..', 'data', 'process',
                               'BRIHN1.GS..sac'))[0]
    BRI_processed = process.rennolet_process(BRI_tr, event_time, BRI_dist)
    last_point = BRI_processed.data[BRI_processed.stats.npts-1]
    np.testing.assert_allclose(last_point, 0, atol=0.0001)


if __name__ == '__main__':
    test_amp_check_trim()
    test_corner_freqs()
    test_all()
