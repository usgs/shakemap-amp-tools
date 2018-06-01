# third party imports
import numpy as np
from obspy.core.stream import Stream

# local imports
from pgm.base import PGM


class PGV(PGM):
    """
    pgv -- Extract Peak Ground Acceleration in %g from input Stream.
    """

    def __init__(self):
        self._units = 'cm/s'

    def getPGM(self, stream, **kwargs):
        """Return PGV value for given input Stream.

        The max velocity from all Trace objects will be returned.
        In the case of a Stream containing data that has been
        converted to (say) Rotd50, then that will presumably be
        a single Trace.

        NB: The input Stream should have already been "processed",
        i.e., filtered, detrended, tapered, etc.)

        Args:
            stream (Obspy Stream): Stream containing one or Traces of
                acceleration data in gals.
            kwargs (**args): Not used in this class.
        Returns:
            tuple: (PGV in cm/s units (float), timeseries with cm/s
                    units (obspy.core.trace.Trace))
        """
        pgm_dict = {}
        pgv_stream = Stream()
        for trace in stream:
            vtrace = trace.copy()
            vtrace.integrate()
            vtrace.stats['units'] = self._units
            pgv = np.abs(vtrace.max())
            pgm_dict[trace.stats['channel']] = pgv
            pgv_stream.append(vtrace)
        return pgm_dict, pgv_stream
