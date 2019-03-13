
import os
from configobj import ConfigObj


def get_output_dir(eventid, debugdir=None):
    """Find ShakeMap event output directory.

    Function for finding output dir based on event ID. This is basically a
    slightly modified and lightweight version of
    shakemap.utils.config.get_config_paths but we don't want to import it
    because it should not be a dependency.


    Args:
        eventid (str):
            Event id.
        debugdir (str):
            Data directory - to be used for testing only.

    """
    if debugdir is None:
        config_file = os.path.join(
            os.path.expanduser('~'),
            '.shakemap',
            'profiles.conf')
        config = ConfigObj(config_file)
        profile_name = config['profile']
        profile = config['profiles'][profile_name]
        # install = profile['install_path']
        data = profile['data_path']
        outputdir = os.path.join(data, eventid, 'current')
        if os.path.exists(outputdir):
            return outputdir
        else:
            return None
    else:
        return debugdir
