# stdlib imports
import warnings

# local imports
from pgm.exception import PGMException
from pgm.gather import get_pgm_classes, group_imcs


def calculate_sa(stream, imcs):
    """
    Calculate the peak ground acceleration.

    Args:
        stream (obspy.core.stream.Stream): streams of strong ground motion.
            Traces in stream must be in units of %%g.
        imcs (list): list of imcs.

    Returns:
        dictionary: Dictionary of sa for different components.
    """
    sa_dict = {}
    # check units and add channel pga
    for trace in stream:
        if trace.stats['units'] != '%%g':
            raise PGMException('Invalid units for sa: %r. '
                               'Units must be %%g' % trace.stats['units'])
    grouped_imcs = group_imcs(imcs)
    # gather imc classes
    pgm_classes = get_pgm_classes('imc')
    # store sa for imcs
    for imc in grouped_imcs:
        if 'calculate_' + imc in pgm_classes:
            sa_func = pgm_classes['calculate_' + imc]
            sa = sa_func(stream, percentiles=grouped_imcs[imc])
            if imc.find('rot') >= 0:
                for percentile in sa:
                    sa_dict[imc.upper() + str(percentile)] = sa[percentile]
            elif imc.find('channels') >= 0:
                for channel in sa:
                    sa_dict[channel] = sa[channel]
            else:
                sa_dict[imc.upper()] = sa
        else:
            warnings.warn('Not a valid IMC: %r. Skipping...' % imc)
    return sa_dict
