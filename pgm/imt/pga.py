# third party imports
import numpy as np
from obspy.core.stream import Stream

# local imports
from pgm.base import PGM


GAL_TO_PCTG = 1 / (9.8)


class PGA(PGM):
    """
    pga -- Extract Peak Ground Acceleration in %g from input Stream.
    """

    def __init__(self):
        self._units = '%%g'

    def getPGM(self, stream, **kwargs):
        """Return PGA value for given input Stream.

        The max acceleration from all Trace
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
            tuple: (PGA in %g units (float), timeseries with %g
                    units (obspy.core.trace.Trace))
        """
        pga_dict = {}
        pga_stream = Stream()
        for trace in stream:
            pga = np.abs(trace.max()) * GAL_TO_PCTG
            pga_trace = trace.copy()
            pga_trace.data = trace.data * GAL_TO_PCTG
            trace.stats['units'] = self._units
            pga_dict[trace.stats['channel']] = pga
            pga_stream.append(pga_trace)
        return pga_dict, pga_stream
