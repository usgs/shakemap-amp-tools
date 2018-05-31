"""Helper functions for processing strong ground motion data"""

def filter_detrend(trace, taper_type='cosine', taper_percentage=0.05,
        filter_type='highpass', filter_frequency=0.02,
        filter_zerophase=True, filter_corners=4):
        """
        Read files from a directory and return stream objects.

        Args:
            trace (obspy.core.trace.Trace): Trace of strong motion data.
            taper_type (str): Type of taper used for processing.
                Default is 'cosine'.
            taper_percentage (float): Maximum taper percentage.
                Default is 0.05.
            filter_type (str): Type of filter used for processing.
                Default is 'highpass'.
            filter_frequency (float): Filter corner frequency.
                Default is 0.02.
            filter_zerophase (bool): If True, applies a forward and backward
                filter. Results in a zero phase shift. Default is True.
            filter_corners (int): Filter corners / order.

        Returns:
            list : List of obspy.core.stream.Stream objects
        """
        trace.detrend('linear')
        trace.detrend('demean')
        trace.taper(max_percentage=taper_percentage, type=taper_type)
        trace.filter(filter_type, freq=filter_frequency,
                     zerophase=filter_zerophase, corners=filter_corners)
        trace.detrend('linear')
        trace.detrend('demean')
        return trace
