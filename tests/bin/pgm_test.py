#!/usr/bin/env python

import subprocess
import os.path
import shutil
import tempfile


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

def test_imc_imt():
    homedir = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(homedir, '..', 'data', 'knet')
    getpgm = os.path.join(homedir,'..','..','bin','getpgm')
    input_format = 'knet'
    imt = '-m pga sa 2 sa 3'
    imc = '-c greater_of_two_horizontals'
    tmpdir = tempfile.mkdtemp()
    try:
        cmd = '%s %s %s %s %s %s' % (getpgm, input_directory,
                tmpdir, input_format, imc, imt)
        res, stdout, stderr = get_command_output(cmd)
        if not res:
            raise AssertionError('getpgm command %s failed with errors "%s"' % (cmd, stderr))
        print(stdout)
    except Exception as e:
        raise(e)
    finally:
        shutil.rmtree(tmpdir)


if __name__ == '__main__':
    test_imc_imt()
