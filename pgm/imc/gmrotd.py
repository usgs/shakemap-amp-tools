import numpy as np

def calculate_gmrotd(stream, percentiles, **kwargs):
    """
    Rotate two horizontal channels using the geometric mean.

    Args:
        stream (obspy.core.stream.Stream): stream of oscillators.
        percentiles (list): list of percentiles (float).
            Example: [100, 50, 75] results in RotD100, RotD50, RotD75.

    Returns:
        obspy.core.trace.Trace: Trace of combined, rotated horizontals.
    """
    horizontals = _get_horizontals(stream)
    if len(horizontals) > 2:
        raise PGMException('More than two horizontal channels.')
    elif len(horizontals) < 2:
        raise PGMException('Less than two horizontal channels.')
    osc1, osc2 = horizontals[0].data, horizontals[1].data
    if len(osc1) != len(osc2):
        raise PGMException

    # Create degree matrices
    degrees = np.deg2rad(np.linspace(0, 90, 91))
    shape = (len(osc1), 1)
    degree_matrix = np.multiply(np.ones(shape), degrees).T
    cos_matrix = np.cos(degree_matrix)
    sin_matrix = np.sin(degree_matrix)

    # Create timeseries matrix
    osc1_matrix = np.multiply(np.ones((91,1)),osc1)
    osc2_matrix = np.multiply(np.ones((91,1)),osc2)

    # Calculate GMs
    osc1_rot = osc1_matrix * cos_matrix + osc2_matrix * sin_matrix
    osc2_rot = osc1_matrix * sin_matrix + osc2_matrix * cos_matrix
    osc1_max = np.amax(osc1_rot, 1)
    osc2_max = np.amax(osc2_rot, 1)
    GMs = np.sqrt(osc1_max * osc2_max)

    # Get percentiles
    GM_percentiles = np.percentile(GMs, percentiles)
    gmrotd_dict = {}
    for idx, percent in enumerate(percentiles):
        gmrotd_dict[percent] = GM_percentiles[idx]
    return gmrotd_dict


def _get_horizontals(stream):
    """
    Gets the two horizontal components

    Args:
        stream (obspy.core.stream.Stream): Strong motion timeseries
            for one station.

    Returns:
        list: list of horizontal channels (obspy.core.trac.Trace)
    """
    horizontal_channels = []
    for idx, trace in enumerate(stream):
        # Group all of the max values from traces without
        # Z in the channel name
        if 'Z' not in trace.stats['channel'].upper():
            horizontal_channels += [trace.copy()]
    return horizontal_channels
