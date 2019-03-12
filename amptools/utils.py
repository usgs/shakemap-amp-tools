# stdlib imports
import os.path
from configobj import ConfigObj


SHAKEMAP_CFG = '.shakemap/profiles.conf'


def get_output_dir(eventid, debugdir=None):
    if debugdir is not None:
        return debugdir
    cfg_file = os.path.join(os.path.expanduser('~'), SHAKEMAP_CFG)
    if not os.path.isfile(cfg_file):
        return None
    config = ConfigObj(cfg_file)
    profile = config['profile']
    data_path = config['profiles'][profile]['data_path']
    datadir = os.path.join(data_path, eventid, 'current')
    if not os.path.isdir(datadir):
        return None
    return datadir
