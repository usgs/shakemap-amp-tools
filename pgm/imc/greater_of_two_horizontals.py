# third party imports
import numpy as np

# local imports
from pgm.base import PGM


GAL_TO_PCTG = 1 / (9.8)


class GREATER_OF_TWO_HORIZONTALS(PGM):
    """
    greater_of_two_horizontals -- imt from two horizontal components.
    """

    def getPGM(self, stream, **kwargs):
        """Return GREATER_OF_TWO_HORIZONTALS value for given input Stream.

        NB: The input Stream should have already been "processed",
        i.e., filtered, detrended, tapered, etc.)

        Args:
            stream (Obspy Stream): Stream containing one or Traces of
                acceleration data in gals.
            kwargs (**args): Units for this class.
        Returns:
            tuple: GREATER_OF_TWO_HORIZONTALS (float), timeseries with greater
                peak value (obspy.core.trace.Trace).
        """
        units = kwargs.get('units', None)
        horizontal_vals = []
        channel_idx = []
        for idx, trace in enumerate(stream):
            # Group all of the max values from traces without
            # Z in the channel name
            if 'Z' not in trace.stats['channel'].upper():
                horizontal_vals += [np.abs(trace.max())]
                channel_idx += [idx]
        greater_idx = np.argmax(np.asarray(horizontal_vals))
        greater_pgm = horizontal_vals[greater_idx]
        if units == '%%g':
            greater_pgm = greater_pgm * GAL_TO_PCTG
        greater_timeseries = stream[greater_idx]
        return greater_pgm, greater_timeseries
