#!/usr/bin/env python

import os.path
import shutil
import tempfile

# third party imports
import pandas as pd
import numpy as np
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

    # # test xlsx
    # columns = excel.to_dict()
    # target_stations = ['AOM001', 'AOM002', 'AOM003', 'AOM004',
    #                    'AOM005', 'AOM006', 'AOM007', 'AOM008',
    #                    'AOM009']
    # stations = [station[0] for station in excel['STATION'].values.tolist()]
    # assert target_stations == stations
    # target_ref = ('Japan National Research Institute '
    #               'for Earth Science and Disaster Resilience')
    # assert target_ref == ref
    # target_network = 'BO'
    # assert excel['NETID'].iloc[0].values[0] == target_network
    # target_latitudes = np.asarray([41.5267, 41.328, 41.4053, 41.4087, 41.2948,
    #                                41.1976, 41.169, 41.084, 40.9665])
    # target_longitudes = np.asarray([140.9244, 140.8132, 141.1691, 141.4486,
    #                                 141.1972, 140.9972, 141.3846, 141.2552,
    #                                 141.3733])
    # lat = np.squeeze(excel['LAT'].values)
    # lon = np.squeeze(excel['LON'].values)
    # np.testing.assert_allclose(lat, target_latitudes, rtol=1e-5)
    # np.testing.assert_allclose(lon, target_longitudes, rtol=1e-5)
    # target_HHZ_pga = np.array([0.2284298, 0.47380254, 0.98515485, 0.70706226, 1.20500181,
    #                            1.47086862, 1.08194606, 1.89994372, 0.95921591])
    # target_HHZ_pgv = np.array([0.19017067, 0.14867001, 0.55684458, 0.26519154, 0.73381456,
    #                            0.63164594, 0.29708227, 0.94268189, 0.49366694])
    # target_HHE_pga = np.array([0.41588284, 1.38591593, 2.29292409, 1.22078135, 2.9645457,
    #                            3.35913078, 3.13269915, 3.08440705, 1.41246878])
    # target_HHE_pgv = np.array([0.35381252, 0.47342173, 1.33228527, 0.4590729, 1.66396918,
    #                            1.34397798, 0.75996718, 1.21127809, 0.65343963])
    # target_HHN_pga = np.array([0.50519133, 1.27025327, 1.76789923, 2.58067363, 2.9390183,
    #                            3.28307859, 2.66145591, 3.68977844, 1.66521052])
    # target_HHN_pgv = np.array([0.28359848, 0.37314823, 1.125286, 0.52449242, 1.62841923,
    #                            1.2848947, 0.59883865, 1.23640865, 1.09028079])
    # HHZ_pga = excel['HNZ']['PGA'].values
    # HHZ_pgv = excel['HNZ']['PGV'].values
    # HHE_pga = excel['HN2']['PGA'].values
    # HHE_pgv = excel['HN2']['PGV'].values
    # HHN_pga = excel['HN1']['PGA'].values
    # HHN_pgv = excel['HN1']['PGV'].values

    # np.testing.assert_allclose(HHZ_pga, target_HHZ_pga, rtol=1e-2)
    # np.testing.assert_allclose(HHZ_pgv, target_HHZ_pgv, rtol=1e-2)
    # np.testing.assert_allclose(HHE_pga, target_HHE_pga, rtol=1e-2)
    # np.testing.assert_allclose(HHE_pgv, target_HHE_pgv, rtol=1e-2)
    # np.testing.assert_allclose(HHN_pga, target_HHN_pga, rtol=1e-2)
    # np.testing.assert_allclose(HHN_pgv, target_HHN_pgv, rtol=1e-2)

    # # TEST for GEONET
    # homedir = os.path.dirname(os.path.abspath(
    #     __file__))  # where is this script?
    # indir = os.path.join(homedir, '..', 'data', 'sm2xml')
    # sm2xml = os.path.join(homedir, '..', '..', 'bin', 'sm2xml')
    # eventid = 'us2018abcd'
    # tmpdir = tempfile.mkdtemp()
    # target_file = os.path.join(tmpdir, 'geonet_' + eventid + '_dat.xml')
    # try:
    #     cmd = '%s %s %s %s -dd' % (sm2xml, eventid, indir, tmpdir)
    #     res, stdout, stderr = get_command_output(cmd)
    #     if not res:
    #         raise AssertionError(
    #             'sm2xml command %s failed with errors "%s"' % (cmd, stderr))
    #     print(stdout)
    #     assert target_file.encode() in stdout
    #     excel, ref = read_excel(target_file.replace('xml', 'xlsx'))
    # except Exception as e:
    #     raise(e)
    # finally:
    #     shutil.rmtree(tmpdir)

    # # test xlsx
    # columns = excel.to_dict()
    # target_stations = ['HSES', 'THZ', 'WPWS', 'WTMC']
    # stations = [station[0] for station in excel['STATION'].values.tolist()]
    # assert stations == target_stations
    # target_source = 'New Zealand Institute of Geological and Nuclear Science'
    # assert ref == target_source
    # target_network = 'NZ'
    # assert excel['NETID'].iloc[0].values[0] == target_network
    # target_latitudes = np.asarray([-41.47666666666667, -40.2375,
    #                                -38.05611111111111, -41.38055555555555])
    # target_longitudes = np.asarray([172.8305555555555, 172.9052777777778,
    #                                 176.5844444444444, 173.0536111111111])
    # lat = np.squeeze(excel['LAT'].values)
    # lon = np.squeeze(excel['LON'].values)
    # np.testing.assert_allclose(lat, target_latitudes, rtol=1e-5)
    # np.testing.assert_allclose(lon, target_longitudes, rtol=1e-5)

    # HHZ_pga_target = np.asarray([16.02178429925751, 2.288236316905321,
    #                              0.2783789422620928, 183.7722265185424])
    # HHZ_pgv_target = np.asarray([9.732713409066722, 4.279438658663453,
    #                              0.08771063001342264, 37.47946982395711])
    # HHZ_sa03_target = np.asarray([46.46565458234634, 6.091350960794354,
    #                               0.3787065133744312, 87.69565329633232])
    # HHZ_sa10_target = np.asarray([12.61000039650761, 4.862407737331735,
    #                               0.03362386754957324, 27.74118062312012])
    # HHZ_sa30_target = np.asarray([3.36218779311461, 2.14553701430188,
    #                               0.003127400241119385, 18.67236895383897])
    # HHZ_pga = excel['HNZ']['PGA'].values
    # HHZ_pgv = excel['HNZ']['PGV'].values
    # HHZ_sa03 = excel['HNZ']['SA(0.3)'].values
    # HHZ_sa10 = excel['HNZ']['SA(1.0)'].values
    # HHZ_sa30 = excel['HNZ']['SA(3.0)'].values

    # np.testing.assert_allclose(HHZ_pga, HHZ_pga_target, rtol=1e-2)
    # np.testing.assert_allclose(HHZ_pgv, HHZ_pgv_target, rtol=1e-2)
    # np.testing.assert_allclose(HHZ_sa03, HHZ_sa03_target, rtol=1e-2)
    # np.testing.assert_allclose(HHZ_sa10, HHZ_sa10_target, rtol=1e-2)
    # np.testing.assert_allclose(HHZ_sa30, HHZ_sa30_target, rtol=1e-2)

    # # Simple run of other formats
    # for file_format in ['smc', 'cwb']:
    #     homedir = os.path.dirname(os.path.abspath(
    #         __file__))  # where is this script?
    #     indir = os.path.join(homedir, '..', 'data', file_format)
    #     sm2xml = os.path.join(homedir, '..', '..', 'bin', 'sm2xml')
    #     eventid = 'us2018abcd'
    #     tmpdir = tempfile.mkdtemp()
    #     target_file = os.path.join(
    #         tmpdir, file_format + '_' + eventid + '_dat.xml')
    #     try:
    #         cmd = '%s %s %s %s -v' % (sm2xml,
    #                                   eventid, indir, tmpdir)
    #         res, stdout, stderr = get_command_output(cmd)
    #         if not res:
    #             fmt = 'sm2xml command %s failed with errors "%s"'
    #             raise AssertionError(fmt % (cmd, stderr))
    #         assert target_file.encode() in stdout
    #     except Exception as e:
    #         raise(e)
    #     finally:
    #         shutil.rmtree(tmpdir)


if __name__ == '__main__':
    test_sm2xml()
