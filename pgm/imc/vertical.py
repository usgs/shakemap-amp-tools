# third party imports
import numpy as np


def calculate_vertical(stream, **kwargs):
    """Return VERTICAL value for given input Stream.

    NB: The input Stream should have already been "processed",
    i.e., filtered, detrended, tapered, etc.)

    Args:
        stream (Obspy Stream): Stream containing one or Traces of
            acceleration data in gals.
        kwargs (**args): Ignored by this class.

    Returns:
        float: VERTICAL.
    """
    vertical = ''
    for trace in stream:
        # Group all of the max values from traces with
        # Z in the channel name
        if 'Z' in trace.stats['channel'].upper():
            vertical = np.abs(trace.max())
    return vertical
