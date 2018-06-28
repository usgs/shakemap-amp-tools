#!/usr/bin/env python

# stdlib imports
import os.path

# local imports
from amptools.io.geonet.core import read_geonet
from pgm.station_summary import StationSummary


def test_gmrotd():
    homedir = os.path.dirname(os.path.abspath(
        __file__))  # where is this script?
    datafile_v2 = os.path.join(homedir, '..', 'data', 'geonet',
                               '20161113_110259_WTMC_20.V2A')
    stream_v2 = read_geonet(datafile_v2)
    station_summary = StationSummary.from_stream(stream_v2,
                                     ['gmrotd50'], ['pga'])
    station_dict = station_summary.pgms['PGA']


if __name__ == '__main__':
    test_gmrotd()
