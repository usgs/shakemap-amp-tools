# third party imports
import numpy as np

# local imports
from pgm.base import PGM


class VERTICAL(PGM):
    """
    vertical -- imt from the vertical component.
    """

    def getPGM(self, stream, **kwargs):
        """Return VERTICAL value for given input Stream.

        NB: The input Stream should have already been "processed",
        i.e., filtered, detrended, tapered, etc.)

        Args:
            stream (Obspy Stream): Stream containing one or Traces of
                acceleration data in gals.
            kwargs (**args): Ignored by this class.
        Returns:
            tuple: (VERTICAL (float), timeseries of vertical
                    component (obspy.core.trace.Trace))
        """
        horizontal_vals = []
        channel_idx = []
        for idx, trace in enumerate(stream):
            # Group all of the max values from traces with
            # Z in the channel name
            if 'Z' in trace.stats['channel'].upper():
                horizontal_vals += [np.abs(trace.max())]
                channel_idx += [idx]
        greater_idx = np.argmax(np.asarray(horizontal_vals))
        greater_pgm = horizontal_vals[greater_idx]
        greater_timeseries = stream[greater_idx]
        return greater_pgm, greater_timeseries
