#!/usr/bin/env python

# stdlib imports
import os.path
import warnings

from amptools.io.dmg.core import is_dmg, read_dmg


def test_dmg():
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    datadir = os.path.join(homedir,'..','..','..','data','dmg')
    file1 = os.path.join(datadir,'CE89146.V2')
    file2 = os.path.join(datadir,'CIWLT.V2')

    for filename in [file1, file2]:
        assert is_dmg(file1)
        
        # test acceleration from the file
        stream1 = read_dmg(filename)

        # test for three traces
        assert stream1.count() == 3

        # test that the traces are acceleration
        for trace in stream1:
            assert trace.stats['units'] == 'acc'

        # test velocity from the file
        stream2 = read_dmg(filename, units='vel')

        # test for three traces
        assert stream2.count() == 3

        # test that the traces are velocity
        for trace in stream2:
            assert trace.stats['units'] == 'vel'

        # test displacement from the file
        stream3 = read_dmg(filename, units='disp')

        # test for three traces
        assert stream3.count() == 3

        # test that the traces are displacement
        for trace in stream3:
            assert trace.stats['units'] == 'disp'

    # Test for wrong format exception
    success = True
    try:
        datadir = os.path.join(homedir,'..','..','..','data','cwb')
        file3 = os.path.join(datadir,'1-EAS.dat')
        read_dmg(file3)
    except Exception:
        success = False
    assert success == False

    # Test for bad date in header warning
    with warnings.catch_warnings(record=True) as w:
        datadir = os.path.join(homedir,'..','..','..','data','dmg')
        file4 = os.path.join(datadir,'BadHeader.V2')
        read_dmg(file4)
        assert issubclass(w[-1].category, Warning)
        assert "Incorrectformat for trigger time" in str(w[-1].message)


if __name__ == '__main__':
    test_dmg()
