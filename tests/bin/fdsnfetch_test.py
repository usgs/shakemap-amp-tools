#!/usr/bin/env python

import subprocess
import os
import glob
import shutil


def get_command_output(cmd):
    """
    Method for calling external system command.

    Args:
        cmd: String command (e.g., 'ls -l', etc.).

    Returns:
        Three-element tuple containing a boolean indicating success or failure,
        the stdout from running the command, and stderr.
    """
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                            )
    stdout, stderr = proc.communicate()
    retcode = proc.returncode
    if retcode == 0:
        retcode = True
    else:
        retcode = False
    return (retcode, stdout, stderr)


def test_fdsnfetch():
    homedir = os.path.dirname(os.path.abspath(__file__))
    fdsnfetch = os.path.join(homedir, '..', '..', 'bin', 'fdsnfetch')

    datadir = os.path.join(homedir, '..', 'data', 'fdsnfetch')
    parameters = 'IRIS 2001-02-28T18:54:32 47.149 -122.7266667 -dmax 0.1'
    cmd_input = '%s %s' % (datadir, parameters)

    cmd = '%s %s' % (fdsnfetch, cmd_input)
    res, stdout, stderr = get_command_output(cmd)
    print(res, stdout, stderr)

    shutil.rmtree(datadir + '/raw')
    shutil.rmtree(datadir + '/resp_cor')

    parameters = 'IRIS 2001-02-28T18:54:32 47.149 -122.7266667 -dmax 1.0'
    parameters += ' -n UW -s ALCT -c EN*'
    cmd_input = '%s %s' % (datadir, parameters)
    cmd = '%s %s' % (fdsnfetch, cmd_input)
    res, stdout, stderr = get_command_output(cmd)
    print(res, stdout, stderr)

    # Confirm that we got the three ALCT station as expected
    os.chdir(datadir)
    os.chdir('raw')
    ALCT_files = glob.glob('UW.ALCT*')
    assert len(ALCT_files) == 3


if __name__ == '__main__':
    test_fdsnfetch()
