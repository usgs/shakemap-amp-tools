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
    
def check_max_amplitude(trace, min_amp=10e-9, max_amp=50):
        """
        Checks that the maximum amplitude of the trace is within a defined
        range.
        
        Args:
            trace (obspy.core.trace.Trace): Trace of strong motion data.
            min_amp (float): Minimum amplitude for the acceptable range.
                Default is 10e-9.
            max_amp (float): Maximum amplitude for the acceptable range.
                Default is 50.
                
        Returns:
            bool: True if trace passes the check. False otherwise.
        """
        
        print(trace.max())
        
        if (abs(trace.max()[0]) >= min_amp and abs(trace.max()[0]) <= max_amp):
            return True
        else:
            return False
        
def trim_to_window(stream, org_time, epi_dist, v_min=1.0):
        """
        Trims a stream of traces to the window using the algorithm
        defined in the Rennolet data paper.
        
        Args: 
            stream (obspy.core.stream.Stream): Stream of strong motion data.
            org_time (UTCDateTime): Event origin time.
            epi_dist (float): Distance from event epicenter to station.
            v_min (float): Minimum apparent velocity.
                Default is 1.0 km/s.
                
        Returns:
            stream (obspy.core.stream.Stream) after windowing.
        """
        end_time = org_time + max(120, epi_dist / v_min)
        stream.trim(endtime=end_time)
        return stream
