#!/usr/bin/env python

# stdlib imports
import os

# third party imports
from obspy import read

# local imports
from pgm.rotation import rotate_pick_method

homedir = os.path.dirname(os.path.abspath(__file__))
datadir = os.path.join(homedir, '..', 'data', 'process')

def test_rotation():

    osc1 = read(os.path.join(datadir, 'ALCTENE.UW..sac'))[0]
    osc2 = read(os.path.join(datadir, 'ALCTENN.UW..sac'))[0]

    rotate_pick_method(osc1, osc2, [50], 'gm')
    rotate_pick_method(osc1, osc2, [50], 'am')
    rotate_pick_method(osc1, osc2, [50], 'max')
    rotate_pick_method(osc1, osc2, [50], 'foo')

if __name__ == '__main__':
    test_rotation()