# stdlib imports
import argparse
import inspect
import warnings

# third party imports
import numpy as np
from obspy.core.stream import Stream
from obspy.core.trace import Trace
from obspy.signal.invsim import simulate_seismometer, corn_freq_2_paz

# local imports
from pgm.base import PGM
from pgm.exception import PGMException


GAL_TO_PCTG = 1 / (9.8)


class SA(PGM):
    """
    sa -- Extract Spectral Response in %g from input Stream.
    """

    def __init__(self):
        self._units = '%%g'

    def getPGM(self, stream, **kwargs):
        """Return SA value for given input Stream.

        The spectral response from all Trace objects will be returned.
        In the case of a Stream containing data that has been converted
        to (say) Rotd50, then that will presumably be a single Trace.

        NB: The input Stream should have already been "processed",
        i.e., filtered, detrended, tapered, etc.)

        Args:
            stream (Obspy Stream): Stream containing one or Traces of
                acceleration data in gals.
            kwargs (**args): Period for this class.
        Returns:
            tuple: (SA in %g units (float), timeseries with %g
                    units (obspy.core.trace.Trace))
        """
        period = kwargs.get('period', None)
        if period is None and not hasattr(self, 'period'):
                raise PGMException('No period specified')
        elif period is not None and hasattr(self, 'period'):
            self.period = period
        elif period is not None:
            self.period = period

        pgm_dict = {}
        sa_stream = Stream()
        for trace in stream:
            samp_rate = trace.stats['sampling_rate']
            sa_trace = self.get_spectral(trace, samp_rate)
            sa = np.abs(sa_trace.max()) * GAL_TO_PCTG
            sa_trace.data = sa_trace.data * GAL_TO_PCTG
            pgm_dict[trace.stats['channel']] = sa
            sa_trace.stats['units'] = self._units
            sa_stream.append(sa_trace)
        return pgm_dict, sa_stream

    def get_spectral(self, trace, samp_rate):
        """Compute ShakeMap pseudo-spectral parameters

        Compute 5% damped PSA at requested period (seconds).

        Args:
            trace (Obspy Trace): Input trace containing acceleration (cm/s**2).
            samp_rate (int or float): Sampling rate (Hz).
        Returns:
            obspy.core.trace.Trace: Trace of spectral response.
        """
        D = 0.05  # 5% damping
        T = self.period

        freq = 1.0 / T
        omega = (2 * 3.14159 * freq) ** 2

        paz_sa = corn_freq_2_paz(freq, damp=D)
        paz_sa['sensitivity'] = omega
        paz_sa['zeros'] = []
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            dd = simulate_seismometer(trace.data, samp_rate, paz_remove=None,
                                      paz_simulate=paz_sa, taper=True,
                                      simulate_sensitivity=True,
                                      taper_fraction=0.05)
        period_str = 'T' + '{:04.2f}'.format(T)
        stats_out = trace.stats.copy()
        stats_out['period'] = period_str
        self.period_str = period_str
        stats_out['channel'] = '%s_%s' % (
            stats_out['channel'], stats_out['period'])
        trace_out = Trace(dd, stats_out)
        return trace_out

    def parseArgs(self, arglist):
        """Parse command line arguments.

        This is the default parseArgs which is sufficient for most
        modules. It will respond to '-h' or '--help' but nothing
        else. If a module needs to accept command line arguments,
        it will need to override this module.

        Args:
            arglist (list): List of potential command line arguments.
        Returns:
            list: Arguments not parsed.
        """
        pgm_name = __name__  # this should be the name of the module
        doc_str = inspect.getdoc(self.__class__)
        parser = argparse.ArgumentParser(prog=pgm_name,
                                         description=doc_str)
        parser.add_argument('period', type=float)
        parser.add_argument('rem', nargs=argparse.REMAINDER,
                            help=argparse.SUPPRESS)
        args = parser.parse_args(arglist)
        if args.period is not None:
            self.period = args.period
        return args.rem
