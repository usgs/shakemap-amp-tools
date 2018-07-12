import numpy as np
from pgm.exception import PGMException


def get_max(tr1, pick_peak, tr2=None, percentiles=50):
    """
    Finds the maximum from traces and either picks the geometric mean,
    arithmetic mean, or maximum of the two. Tr1 and Tr2 can either be
    1d traces, or a 2d rotated matrix. The axis along which to pick the
    maximums is chosen by the dimensions of the input.

    Args:
        tr1 (obspy.core.trace.Trace or 2D array): Trace 1, either 1d trace or
            2d rotation matrix
        tr2 (obspy.core.trace.Trace or 2D array): Trace 2, either 1d trace or
            2d rotation matrix
        pick_peak (str): The choice for either geometric mean, arithmetic
            or maximum. The valid strings are:
                - "gm" for geometric mean
                - "am" for arithmetic mean
                - "max" for maximum

    Returns:
        If 1D input:
            Returns a singular,  scalar value for the requested pick_peak.
        If 2D input:
            Returns a list of the maximum values, as well as the singular value
            at the requested percentile
    """

    # Check if valid trace dimensions were provided, and determine if we're
    # working with 1D or 2D traces. Trace 1 and Trace 2 must have the same
    # dimension (either both 1D or 2D).
    if tr2 is None:
        if (len(tr1.shape) == 1):
            input_dim = '1D'
        elif (len(tr1.shape) == 2):
            input_dim = '2D'
        else:
            raise PGMException('Trace one must be either 1D or 2D.')
    else:
        if (len(tr1.shape) != len(tr2.shape)):
            raise PGMException('Traces must have the same dimensions.')
        elif (len(tr1.shape) == 1):
            input_dim = '1D'
        elif (len(tr1.shape) == 2):
            input_dim = '2D'
        else:
            raise PGMException('Traces must be either 1D or 2D.')

    # Set the axis from which to pull the maximums based on
    # the input dimension.
    if input_dim == '1D':
        axis = 0
    else:
        axis = 1

    # Geometric mean
    if (pick_peak.lower() == 'gm'):
        tr1_max = np.amax(tr1, axis)
        tr2_max = np.amax(tr2, axis)
        geo_means = np.sqrt(tr1_max * tr2_max)

        if (input_dim == '1D'):
            return geo_means
        else:
            return geo_means, np.percentile(geo_means, percentiles)

    # Arithmetic mean
    elif (pick_peak.lower() == 'am'):
        tr1_max = np.amax(tr1, axis)
        tr2_max = np.amax(tr2, axis)
        arith_means = 0.5 * (tr1_max + tr2_max)

        if (input_dim == '1D'):
            return arith_means
        else:
            return arith_means, np.percentile(arith_means, percentiles)

    # Maximum
    elif (pick_peak.lower() == 'max'):
        if tr2 is not None:
            tr1_max = np.amax(np.abs(tr1), axis)
            tr2_max = np.amax(np.abs(tr2), axis)

            # Maximum of two horizontals
            if (input_dim == '1D'):
                return np.amax([tr1_max, tr2_max])
            else:
                maximums = []
                for idx, val in enumerate(tr1_max):
                    max_val = np.max([val, tr2_max[idx]])
                    maximums.append(max_val)
                return maximums, np.percentile(maximums, percentiles)
        else:
            maximums = np.amax(np.abs(tr1), axis)
            if (input_dim == '1D'):
                return maximums
            else:
                return maximums, np.percentile(maximums, percentiles)
    else:
        raise PGMException('Not a valid pick for the peak.')


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
