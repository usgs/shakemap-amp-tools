import numpy as np
import warnings

def rotate_pick_method(tr1, tr2, percentiles, method_pick):

    # GMRotD
    if (method_pick.lower() == 'gm'):
        tr1_rot, tr2_rot = rotate(tr1, tr2, combine=False)
        tr1_max = np.amax(tr1_rot, 1)
        tr2_max = np.amax(tr2_rot, 1)
        geo_means = np.sqrt(tr1_max * tr2_max)
        return geo_means, np.percentile(geo_means, percentiles)

    # Arithmetic mean RotD
    elif (method_pick.lower() == 'am'):
        tr1_rot, tr2_rot = rotate(tr1, tr2, combine=False)
        tr1_max = np.amax(tr1_rot, 1)
        tr2_max = np.amax(tr2_rot, 1)
        arith_means = 0.5 * (tr1_max + tr2_max)
        return arith_means, np.percentile(arith_means, percentiles)

    # RotD
    elif (method_pick.lower() == 'max'):
        rot = rotate(tr1, tr2, combine=True)
        maximums = np.amax(np.abs(rot), 1)
        return maximums, np.percentile(maximums, percentiles)

    else:
        warnings.warn('Not a valid method pick. Rotation will not be calculated.')
        return


def rotate(tr1, tr2, combine=False):
    """
    Rotates a trace through 180 degrees to obtain the
    data at each degree.

    Args:
        tr1 (obspy.core.trace.Trace): Trace 1 of strong motion data.
        tr2 (obspy.core.trace.Trace): Trace 2 of strong motion data.
        percentiles (list): Percentiles of the data that should be returned.
        geo_mean (bool): Whether or not GMRotD should be calculated.
        arith_mean (bool):
        maximum (bool:
        combine (bool): Whether rotated traces should be combined.

    Returns:
        numpy.ndarray: Array of data at each degree.
    """
    if combine:
        degrees = np.deg2rad(np.linspace(0, 180, 181))
        shape = (len(tr1), 1)
        degree_matrix = np.multiply(np.ones(shape), degrees).T
        cos_matrix = np.cos(degree_matrix)
        sin_matrix = np.sin(degree_matrix)

        # Create timeseries matrix
        osc1_matrix = np.multiply(np.ones((181, 1)), tr1)
        osc2_matrix = np.multiply(np.ones((181, 1)), tr2)

        # Calculate GMs
        rot = osc1_matrix * cos_matrix + osc2_matrix * sin_matrix
        return rot

    else:
        degrees = np.deg2rad(np.linspace(0, 90, 91))
        shape = (len(tr1), 1)
        degree_matrix = np.multiply(np.ones(shape), degrees).T
        cos_matrix = np.cos(degree_matrix)
        sin_matrix = np.sin(degree_matrix)

        # Create timeseries matrix
        osc1_matrix = np.multiply(np.ones((91, 1)), tr1)
        osc2_matrix = np.multiply(np.ones((91, 1)), tr2)

        # Calculate GMs with rotation
        osc1_rot = osc1_matrix * cos_matrix + osc2_matrix * sin_matrix
        osc2_rot = osc1_matrix * sin_matrix + osc2_matrix * cos_matrix
        return osc1_rot, osc2_rot