#!/usr/bin/env python

import subprocess
import os.path
import shutil
import tempfile

from impactutils.io.cmd import get_command_output


def test_amps2xml():
    homedir = os.path.dirname(os.path.abspath(
        __file__))  # where is this script?
    excelfile = os.path.join(homedir, '..', 'data', 'minimum_mmi.xlsx')
    amps2xml = os.path.join(homedir, '..', '..', 'bin', 'amps2xml')
    tmpdir = tempfile.mkdtemp()

    try:
        cmd = '%s foo --debug-dir=%s %s' % (amps2xml, tmpdir, excelfile)
        res, stdout, stderr = get_command_output(cmd)
        if not res:
            raise AssertionError(
                'amps2xml command %s failed with errors "%s"' % (cmd, stderr))
        print(stdout)
    except Exception as e:
        raise(e)
    finally:
        shutil.rmtree(tmpdir)


if __name__ == '__main__':
    test_amps2xml()
