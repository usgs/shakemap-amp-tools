#!/usr/bin/env python

# stdlib imports
import os.path
import numpy as np

# third party imports
from obspy.core.stream import read
from obspy.core.utcdatetime import UTCDateTime
from amptools import process

homedir = os.path.dirname(os.path.abspath(__file__))
datadir = os.path.join(homedir, '..', 'data', 'process')


def test_amp_check_trim():

    # read the two sac files for testing
    # one is unedited with a standard maximum amplitude
    # the second has been multiplied so that it fails the amplitude check
    NOWS_tr = read(os.path.join(datadir, 'NOWSENR.sac'))[0]
    NOWS_tr_mul = read(os.path.join(datadir, 'NOWSENR_mul.sac'))[0]

    assert process.check_max_amplitude(NOWS_tr) is True
    assert process.check_max_amplitude(NOWS_tr_mul) is False

    # Check that our trim and window function doesn't affect the ending time
    # of this record
    org_time = UTCDateTime('2001-02-14T22:03:58')
    trim = process.trim_total_window(NOWS_tr, org_time, 32.7195).stats.endtime
    assert NOWS_tr.stats.endtime == trim


def test_corner_freqs():
    event_time = UTCDateTime('2001-02-28T18:54:32')
    ALCT_tr = read(os.path.join(datadir, 'ALCTENE.UW..sac'))[0]
    ALCT_dist = 75.9559

    GNW_tr = read(os.path.join(datadir, 'GNWBHE.UW..sac'))[0]
    GNW_dist = 46.7473

    corners_1 = process.get_corner_frequencies(ALCT_tr, event_time, ALCT_dist)
    np.testing.assert_allclose(corners_1, [0.03662, 50.0], atol=0.001)

    corners_2 = process.get_corner_frequencies(GNW_tr, event_time, GNW_dist)
    np.testing.assert_allclose(corners_2, [0.03662, 25.0], atol=0.001)

    event_time = UTCDateTime('2016-10-22T17:17:05')
    ALKI_tr = read(os.path.join(datadir, 'ALKIENE.UW..sac'))[0]
    ALKI_dist = 37.87883

    corners_3 = process.get_corner_frequencies(ALKI_tr, event_time, ALKI_dist)
    np.testing.assert_allclose(corners_3, [-2, -2], atol=0)


def test_all():
    # Get our data directory
    event_time = UTCDateTime('2003-01-15T03:41:58')
    HAWA_dist = 80.1893
    HAWA_tr = read(os.path.join(datadir, 'HAWABHN.US..sac'))[0]
    HAWA_processed = process.process_all(HAWA_tr, event_time, HAWA_dist)
    # Load in the already calculated array form processing
    HAWA_array = np.genfromtxt(os.path.join(datadir,
                                            'HAWABHN.US..sac.acc.final.txt'),
                               dtype=float)
    HAWA_array = HAWA_array.T
    HAWA_calc_data = HAWA_array[1]

    # Compare the processing script with the already processed data
    np.testing.assert_allclose(HAWA_processed.data, HAWA_calc_data, atol=0.001)

    # Test file that will conduct low-pass filter
    event_time = UTCDateTime('2001-02-28T18:54:32')
    BRI_dist = 55.6385
    BRI_tr = read(os.path.join(datadir, 'BRIHN1.GS..sac'))[0]
    process.process_all(BRI_tr, event_time, BRI_dist)

    # Triggers the invalid low pass filtering warning
    event_time = UTCDateTime('2001-02-28T18:54:32')
    ALCT_dist = 75.9559
    ALCT_tr = read(os.path.join(datadir, 'ALCTENE.UW..sac'))[0]
    process.process_all(ALCT_tr, event_time, ALCT_dist)

    GNW_tr = read(os.path.join(datadir, 'GNWBHE.UW..sac'))[0]
    GNW_dist = 46.7473
    process.process_all(GNW_tr, event_time, GNW_dist)

    # Test trace with invalid amplitudes
    NOWS_tr_mul = read(os.path.join(datadir, 'NOWSENR_mul.sac'))[0]
    time = UTCDateTime('2001-02-14T22:03:58')
    dist = 50.05
    assert process.process_all(NOWS_tr_mul, time, dist) is None

    # Test trace with low S/N ratio
    event_time = UTCDateTime('2016-10-22T17:17:05')
    ALKI_tr = read(os.path.join(datadir, 'ALKIENE.UW..sac'))[0]
    ALKI_dist = 37.87883
    ALKI_processed = process.process_all(ALKI_tr, event_time, ALKI_dist)
    assert ALKI_processed is None

    # Test with invalid starttime
    ALKI_tr.stats.starttime += 500
    assert process.process_all(ALKI_tr, event_time, ALKI_dist) is None

    ALKI_split = process.split_signal_and_noise(ALKI_tr, event_time, ALKI_dist)
    assert ALKI_split == (-1, -1)


if __name__ == '__main__':
    test_amp_check_trim()
    test_corner_freqs()
    test_all()
