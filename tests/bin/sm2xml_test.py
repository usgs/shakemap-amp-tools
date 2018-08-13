#!/usr/bin/env python

import subprocess
import os.path
import shutil
import tempfile

# third party imports
import pandas as pd
import numpy as np


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


def test_sm2xml():
    # TEST for KNET
    homedir = os.path.dirname(os.path.abspath(
        __file__))  # where is this script?
    indir = os.path.join(homedir, '..', 'data', 'knet')
    sm2xml = os.path.join(homedir, '..', '..', 'bin', 'sm2xml')
    eventid = 'us2018abcd'
    coords = [142.5, 41.0]
    tmpdir = tempfile.mkdtemp()
    target_file = os.path.join(tmpdir, 'knet_' + eventid + '_dat.xml')
    try:
        cmd = '%s %s %s %s -c %s %s -d' % (sm2xml, eventid, indir,
                tmpdir, coords[0], coords[1])
        res, stdout, stderr = get_command_output(cmd)
        if not res:
            raise AssertionError(
                'sm2xml command %s failed with errors "%s"' % (cmd, stderr))
        print(stdout)
        assert target_file.encode() in stdout
        excel = pd.read_excel(target_file.replace('xml', 'xlsx'))
    except Exception as e:
        raise(e)
    finally:
        shutil.rmtree(tmpdir)

    # test xlsx
    columns = excel.to_dict()
    target_stations = np.asarray(['AOM001', 'AOM002', 'AOM003', 'AOM004',
                                  'AOM005', 'AOM006', 'AOM007', 'AOM008',
                                  'AOM009'])
    for idx in range(3, len(columns['Reference'])):
        assert columns['Reference'][idx] == target_stations[idx-3]
    target_source = ('Japan National Research Institute '
                     'for Earth Science and Disaster Resilience')
    for idx in range(3, len(columns['Unnamed: 2'])):
        assert columns['Unnamed: 2'][idx] == target_source
    target_network = 'BO'
    for idx in range(3, len(columns['Unnamed: 3'])):
        assert columns['Unnamed: 3'][idx] == target_network
    target_latitudes = np.asarray([41.5267, 41.328, 41.4053, 41.4087, 41.2948,
                                   41.1976, 41.169, 41.084, 40.9665])
    target_longitudes = np.asarray([140.9244, 140.8132, 141.1691, 141.4486,
                                    141.1972, 140.9972, 141.3846, 141.2552,
                                    141.3733])
    assert len(columns['Unnamed: 4']) == len(columns['Unnamed: 5'])
    lat = []
    lon = []
    for idx in range(3, len(columns['Unnamed: 4'])):
        lat += [columns['Unnamed: 4'][idx]]
        lon += [columns['Unnamed: 5'][idx]]
    np.testing.assert_allclose(np.asarray(lat), target_latitudes, rtol=1e-5)
    np.testing.assert_allclose(np.asarray(lon), target_longitudes, rtol=1e-5)
    target_HHZ_pga = np.asarray([0.228584809, 0.47412405, 0.985823343,
                                 0.707542051, 1.20581949, 1.471866709,
                                 1.082680233, 1.901232967, 0.959866807])
    target_HHZ_pgv = np.asarray([0.190170671, 0.148670008, 0.556844579,
                                 0.265191543, 0.733814558, 0.631645945,
                                 0.297082273, 0.942681894, 0.493666936])
    target_HHE_pga = np.asarray([0.416165047, 1.386856374, 2.294479998,
                                 1.221609736, 2.96655736, 3.361410193,
                                 3.134824907, 3.086500037, 1.413427245])
    target_HHE_pgv = np.asarray([0.353812522, 0.473421728, 1.332285268,
                                 0.459072902, 1.663969182, 1.343977981,
                                 0.759967176, 1.211278091, 0.653439633])
    target_HHN_pga = np.asarray([0.50553414, 1.271115232, 1.769098873,
                                 2.582424804, 2.941012635, 3.285306389,
                                 2.663261897, 3.692282223, 1.666340485])
    target_HHN_pgv = np.asarray([0.283598475, 0.373148229, 1.125286,
                                 0.524492418, 1.628419234, 1.284894696,
                                 0.59883865, 1.236408648, 1.090280786])
    HHZ_pga = []
    HHZ_pgv = []
    HHE_pga = []
    HHE_pgv = []
    HHN_pga = []
    HHN_pgv = []
    for idx in range(3, len(columns['Unnamed: 6'])):
        HHZ_pga += [columns['Unnamed: 7'][idx]]
        HHZ_pgv += [columns['Unnamed: 8'][idx]]
        HHE_pga += [columns['Unnamed: 12'][idx]]
        HHE_pgv += [columns['Unnamed: 13'][idx]]
        HHN_pga += [columns['Unnamed: 17'][idx]]
        HHN_pgv += [columns['Unnamed: 18'][idx]]
    np.testing.assert_allclose(np.asarray(HHZ_pga), target_HHZ_pga, rtol=1e-2)
    np.testing.assert_allclose(np.asarray(HHZ_pgv), target_HHZ_pgv, rtol=1e-2)
    np.testing.assert_allclose(np.asarray(HHE_pga), target_HHE_pga, rtol=1e-2)
    np.testing.assert_allclose(np.asarray(HHE_pgv), target_HHE_pgv, rtol=1e-2)
    np.testing.assert_allclose(np.asarray(HHN_pga), target_HHN_pga, rtol=1e-2)
    np.testing.assert_allclose(np.asarray(HHN_pgv), target_HHN_pgv, rtol=1e-2)

    # TEST for GEONET
    homedir = os.path.dirname(os.path.abspath(
        __file__))  # where is this script?
    indir = os.path.join(homedir, '..', 'data', 'geonet')
    sm2xml = os.path.join(homedir, '..', '..', 'bin', 'sm2xml')
    eventid = 'us2018abcd'
    tmpdir = tempfile.mkdtemp()
    target_file = os.path.join(tmpdir, 'geonet_' + eventid + '_dat.xml')
    try:
        cmd = '%s %s %s %s -dd' % (sm2xml, eventid, indir, tmpdir)
        res, stdout, stderr = get_command_output(cmd)
        if not res:
            raise AssertionError(
                'sm2xml command %s failed with errors "%s"' % (cmd, stderr))
        print(stdout)
        assert target_file.encode() in stdout
        excel = pd.read_excel(target_file.replace('xml', 'xlsx'))
    except Exception as e:
        raise(e)
    finally:
        shutil.rmtree(tmpdir)

    # test xlsx
    columns = excel.to_dict()
    target_stations = np.asarray(['WTMC', 'HSES', 'THZ', 'WPWS'])
    for idx in range(3, len(columns['Reference'])):
        assert columns['Reference'][idx] == target_stations[idx-3]
    target_source = 'New Zealand Institute of Geological and Nuclear Science'
    for idx in range(3, len(columns['Unnamed: 2'])):
        assert columns['Unnamed: 2'][idx] == target_source
    target_network = 'NZ'
    for idx in range(3, len(columns['Unnamed: 3'])):
        assert columns['Unnamed: 3'][idx] == target_network
    target_latitudes = np.asarray([-41.38055556, -41.47666667,
                                   -40.2375, -38.05611111])
    target_longitudes = np.asarray([173.0536111, 172.8305556,
                                    172.9052778, 176.5844444])
    assert len(columns['Unnamed: 4']) == len(columns['Unnamed: 5'])
    lat = []
    lon = []
    for idx in range(3, len(columns['Unnamed: 4'])):
        lat += [columns['Unnamed: 4'][idx]]
        lon += [columns['Unnamed: 5'][idx]]
    np.testing.assert_allclose(np.asarray(lat), target_latitudes, rtol=1e-5)
    np.testing.assert_allclose(np.asarray(lon), target_longitudes, rtol=1e-5)
    HHZ_pga_target = np.asarray([183.8969291, 16.03265622, 2.289789049,
                                 0.278567842])
    HHZ_pgv_target = np.asarray([37.47946982, 9.732713409, 4.279438659,
                                 0.08771063])
    HHZ_sa03_target = np.asarray([88.13527156, 47.19331741, 6.115072067,
                                  0.380902713])
    HHZ_sa10_target = np.asarray([27.47415841, 12.63667365, 4.820458073,
                                  0.033118346])
    HHZ_sa30_target = np.asarray([18.47655605, 3.369270248, 2.202909935,
                                  0.002717927])
    HHZ_pga = []
    HHZ_pgv = []
    HHZ_sa03 = []
    HHZ_sa10 = []
    HHZ_sa30 = []
    for idx in range(3, len(columns['Unnamed: 6'])):
        HHZ_pga += [columns['Unnamed: 6'][idx]]
        HHZ_pgv += [columns['Unnamed: 7'][idx]]
        HHZ_sa03 += [columns['Unnamed: 8'][idx]]
        HHZ_sa10 += [columns['Unnamed: 9'][idx]]
        HHZ_sa30 += [columns['Unnamed: 10'][idx]]
    np.testing.assert_allclose(np.asarray(HHZ_pga), HHZ_pga_target, rtol=1e-2)
    np.testing.assert_allclose(np.asarray(HHZ_pgv), HHZ_pgv_target, rtol=1e-2)
    np.testing.assert_allclose(np.asarray(
        HHZ_sa03), HHZ_sa03_target, rtol=1e-2)
    np.testing.assert_allclose(np.asarray(
        HHZ_sa10), HHZ_sa10_target, rtol=1e-2)
    np.testing.assert_allclose(np.asarray(
        HHZ_sa30), HHZ_sa30_target, rtol=1e-2)

    # Simple run of other formats
    for file_format in ['smc', 'cwb']:
        homedir = os.path.dirname(os.path.abspath(
            __file__))  # where is this script?
        indir = os.path.join(homedir, '..', 'data', file_format)
        sm2xml = os.path.join(homedir, '..', '..', 'bin', 'sm2xml')
        eventid = 'us2018abcd'
        tmpdir = tempfile.mkdtemp()
        target_file = os.path.join(
            tmpdir, file_format + '_' + eventid + '_dat.xml')
        try:
            cmd = '%s %s %s %s -v' % (sm2xml,
                                      eventid, indir, tmpdir)
            res, stdout, stderr = get_command_output(cmd)
            if not res:
                fmt = 'sm2xml command %s failed with errors "%s"'
                raise AssertionError(fmt % (cmd, stderr))
            assert target_file.encode() in stdout
        except Exception as e:
            raise(e)
        finally:
            shutil.rmtree(tmpdir)


if __name__ == '__main__':
    test_sm2xml()
