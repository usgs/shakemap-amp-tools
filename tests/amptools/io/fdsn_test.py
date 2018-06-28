#!/usr/bin/env python

import os
import numpy as np
from amptools.io.fdsn import request_raw_waveforms, remove_response
from amptools import process

homedir = os.path.dirname(os.path.abspath(__file__))
datadir = os.path.join(homedir, '..', '..', 'data', 'process')


def test_fetch():
    nisqually_st = request_raw_waveforms('IRIS', '2001-02-28T18:54:32',
                                         47.149, -122.7266667,
                                         dist_max=0.4, after_time=120)

    # Set one of the waveforms to have a clipped value
    nisqually_st[0].data[0] = 2000000
    clips_length = len(nisqually_st)

    nisqually_bas_cor = process.correct_baseline_mean(nisqually_st)
    nisqually_clip_rm = process.remove_clipped(nisqually_bas_cor)
    nisqually_resp_rm = remove_response(nisqually_clip_rm)

    # Test that this stream we requested gives us the same PGA as
    # calculated previously
    test_fdsn = nisqually_resp_rm[3]
    np.testing.assert_allclose(abs(test_fdsn.max()), 1.48, atol=0.01)

    # Test to make sure that the clipped waveform was removed from the stream
    no_clips_length = len(nisqually_resp_rm)
    assert no_clips_length < clips_length


if __name__ == '__main__':
    test_fetch()
