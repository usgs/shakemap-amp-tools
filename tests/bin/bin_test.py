#!/usr/bin/env python

import subprocess
import pandas as pd
from xml.dom import minidom
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

def test_amps2xml():
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    excelfile = os.path.join(homedir,'..','data','minimum_mmi.xlsx')
    amps2xml = os.path.join(homedir,'..','..','bin','amps2xml')
    tmpdir = tempfile.mkdtemp()
    try:
        cmd = '%s %s %s' % (amps2xml,excelfile,tmpdir)
        res,stdout,stderr = get_command_output(cmd)
        if not res:
            raise AssertionError('amps2xml command %s failed with errors "%s"' % (cmd,stderr))
        print(stdout)
    except Exception as e:
        raise(e)
    finally:
        shutil.rmtree(tmpdir)

def test_sm2xml():
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    indir = os.path.join(homedir,'..','data','knet')
    sm2xml = os.path.join(homedir,'..','..','bin','sm2xml')
    eventid = 'us2018abcd'
    tmpdir = tempfile.mkdtemp()
    dformat = 'knet'
    try:
        cmd = '%s %s %s %s %s' % (sm2xml,eventid,indir,tmpdir,dformat)
        res,stdout,stderr = get_command_output(cmd)
        if not res:
            raise AssertionError('sm2xml command %s failed with errors "%s"' % (cmd,stderr))
        print(stdout)
    except Exception as e:
        raise(e)
    finally:
        shutil.rmtree(tmpdir)
        
if __name__ == '__main__':
    test_amps2xml()
    test_sm2xml()
