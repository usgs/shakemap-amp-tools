#!/usr/bin/env python

# stdlib imports
import os.path

# third party imports
from obspy.core.stream import read
from obspy.core.utcdatetime import UTCDateTime
from amptools.process import check_max_amplitude, trim_to_window


homedir = os.path.dirname(os.path.abspath(__file__))

NOWS_tr = read(os.path.join(homedir, '..', 'data', 'process', 'NOWSENR.sac'))
NOWS_tr_mul  = read(os.path.join(homedir, '..', 'data', 'process', 'NOWSENR_mul.sac'))

assert check_max_amplitude(NOWS_tr) == True
assert check_max_amplitude(NOWS_tr_mul) == False

assert NOWS_tr[0].stats.endtime == trim_to_window(NOWS_tr, UTCDateTime('2001-02-14T22:03:58'), 32.7195)[0].stats.endtime