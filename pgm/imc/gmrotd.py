from pgm.exception import PGMException
from pgm.rotation import rotate_pick_method


def calculate_gmrotd(stream, percentiles, **kwargs):
    """
    Rotate two horizontal channels using the geometric mean.

    Args:
        stream (obspy.core.stream.Stream): stream of oscillators.
        percentiles (list): list of percentiles (float).
            Example: [100, 50, 75] results in RotD100, RotD50, RotD75.

    Returns:
        dictionary: Dictionary of geometric mean for each percentile.
    """
    horizontals = _get_horizontals(stream)
    if len(horizontals) > 2:
        raise PGMException('More than two horizontal channels.')
    elif len(horizontals) < 2:
        raise PGMException('Less than two horizontal channels.')
    osc1, osc2 = horizontals[0].data, horizontals[1].data
    if len(osc1) != len(osc2):
        raise PGMException

    geo_means, gm_percentiles = rotate_pick_method(osc1, osc2,
                                                   percentiles, 'gm')

    gmrotd_dict = {}
    for idx, percent in enumerate(percentiles):
        gmrotd_dict[percent] = gm_percentiles[idx]
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
    for _, trace in enumerate(stream):
        # Group all of the max values from traces without
        # Z in the channel name
        if 'Z' not in trace.stats['channel'].upper():
            horizontal_channels += [trace.copy()]
    return horizontal_channels
