#!/usr/bin/env python

import os.path
import shutil
import tempfile

# third party imports
from impactutils.io.cmd import get_command_output

# local imports
# from impactutils.io.table import read_excel


def test_sm2xml():
    # TEST for KNET
    homedir = os.path.dirname(os.path.abspath(
        __file__))  # where is this script?
    indir = os.path.join(homedir, '..', 'data', 'geonet')
    sm2xml = os.path.join(homedir, '..', '..', 'bin', 'sm2xml')
    eventid = 'us1000778i'
    tmpdir = tempfile.mkdtemp()
    try:
        cmd = '%s %s %s --debug-dir=%s' % (sm2xml, eventid, indir, tmpdir)
        res, stdout, stderr = get_command_output(cmd)
        if not res:
            raise AssertionError(
                'sm2xml command %s failed with errors "%s"' % (cmd, stderr))
        print(stdout)
        # assert target_file.encode() in stdout
        # excel, ref = read_excel(target_file.replace('xml', 'xlsx'))
    except Exception as e:
        raise(e)
    finally:
        shutil.rmtree(tmpdir)


if __name__ == '__main__':
    test_sm2xml()
