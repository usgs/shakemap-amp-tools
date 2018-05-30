# third party imports
import numpy as np

# local imports
from .base import PGM

GAL_TO_PCTG = 1 / (9.8)


class PGA(PGM):
    """
    pga -- Extract Peak Ground Acceleration in %g from input Stream.
    """

    def __init__(self):
        self.units = '%%g'

    def getPGM(self, stream, **kwargs):
        """Return PGA value for given input Stream.

        The max acceleration from all horizontal Trace
        objects will be returned.  In the case of a Stream
        containing data that has been converted to (say) Rotd50,
        then that will presumably be a single Trace.

        NB: The input Stream should have already been "processed",
        i.e., filtered, detrended, tapered, etc.)

        Args:
            stream (Obspy Stream): Stream containing one or Traces of
                acceleration data in gals.
            kwargs (**args): Not used in this class.
        Returns:
            float: PGA in %g units.
        """
        pgm_dict = {}
        for trace in stream:
            pga = np.abs(trace.max()) * GAL_TO_PCTG
            pgm_dict[trace.stats['channel']] = pga

        return pgm_dict
