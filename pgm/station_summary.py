# stdlib imports
from collections import OrderedDict
import warnings
import re

# third party imports
import numpy as np
from obspy.core.stream import Stream
from obspy.core.trace import Trace
from obspy.signal.invsim import corn_freq_2_paz, simulate_seismometer
import pandas as pd

# local imports
from pgm.imt.pga import calculate_pga
from pgm.imt.pgv import calculate_pgv
from pgm.imt.sa import calculate_sa


GAL_TO_PCTG = 1 / (9.8)


class StationSummary(object):
    """
    Class for returning pgm values for specific components.
    """

    def __init__(self, stream, components, imts, damping=0.05):
        """
        Args:
            stream (obspy.core.stream.Stream): Strong motion timeseries
                for one station.
            components (list): List of requested components (str).
            imts (list): List of requested imts (str).
            damping (float): Damping of oscillator. Default is 5% (0.05)

        Note:
            Assumes a processed stream with units of gal (1 cm/s^2).
            No processing is done by this class.
        """
        self.components = set(np.sort(components))
        self.damping = damping
        self.imts = set(np.sort(imts))
        self.stream = stream
        # Get oscillators
        self.oscillators = self.generate_oscillators()
        # Gather pgm/imt for each
        self.pgms = self.gather_pgms()

    def create_flatfile_rows(self):
        """
        Creates a dataframe table similar to a flatfile where each row
        is a channel/component.

        Returns:
            pandas.DataFrame: Flatfile-like table.

        Notes:
            Assumes generate_oscillators and gather_pgms has already been
            called for this class instance.
            Headers:
                - Record Sequence Number
                - YEAR
                - MODY
                - HRMN
                - Station Name
                - Station ID  No.
                - Station Latitude
                - Station Longitude
                - Channel
                - All requested PGM values (one type per column)
                ...
        """
        pgms = self.pgms.copy()
        dataframe_dict = OrderedDict()
        # Initialize dataframe headers
        columns = ['Record Sequence Number', 'YEAR', 'MODY', 'HRMN',
                   'Station Name', 'Station ID  No.', 'Station Latitude',
                   'Station Longitude', 'Channel']
        imt_keys = [val for val in pgms]
        for imt_key in np.sort(imt_keys):
            columns += [imt_key]
        for col in columns:
            dataframe_dict[col] = []

        imc_keys = [val for val in pgms[imt_keys[0]]]
        # Set metadata
        stats = self.stream[0].stats
        counter = 0
        for imc in np.sort(imc_keys):
            counter += 1
            dataframe_dict['YEAR'] += [stats['starttime'].year]
            # Format the date
            dataframe_dict['Record Sequence Number'] += [counter]
            month = '{:02d}'.format(stats['starttime'].month)
            day = '{:02d}'.format(stats['starttime'].day)
            dataframe_dict['MODY'] += [month + day]
            hour = '{:02d}'.format(stats['starttime'].hour)
            minute = '{:02d}'.format(stats['starttime'].minute)
            dataframe_dict['HRMN'] += [hour + minute]
            try:
                station_str = stats['standard']['station_name']
            except KeyError:
                station_str = stats['name']
            dataframe_dict['Station Name'] = [station_str]
            dataframe_dict['Station ID  No.'] += [stats['station']]
            try:
                latitude = stats['coordinates']['latitude']
            except KeyError:
                latitude = stats['lat']
            dataframe_dict['Station Latitude'] += [latitude]
            try:
                longitude = stats['coordinates']['longitude']
            except KeyError:
                longitude = stats['lon']
            dataframe_dict['Station Longitude'] += [longitude]
            dataframe_dict['Channel'] += [imc]
            for imt_key in np.sort(imt_keys):
                dataframe_dict[imt_key] += [pgms[imt_key][imc]]
        # Create pandas dataframe
        dataframe = pd.DataFrame(data=dataframe_dict)
        return dataframe

    def create_table(self):
        """
        Creates a dataframe table of IMC vs IMT.

        Returns:
            pandas.DataFrame: Table of IMC vs IMT.

        Notes:
            Assumes generate_oscillators and gather_pgms has already been
            called for this class instance.
        """
        pgms = self.pgms.copy()
        # Initialize dataframe headers
        dataframe_dict = OrderedDict()
        dataframe_dict[''] = []
        imt_keys = np.sort([val for val in pgms])
        imc_keys = np.sort([val for val in pgms[imt_keys[0]]])
        for imc_key in imc_keys:
            dataframe_dict[imc_key] = []
        for imt_key in imt_keys:
            dataframe_dict[''] += [imt_key]
        # Create dataframe
        for imc_key in imc_keys:
            for imt_key in imt_keys:
                dataframe_dict[imc_key] += [pgms[imt_key][imc_key]]
        # Create pandas dataframe
        dataframe = pd.DataFrame(data=dataframe_dict)
        return dataframe

    def gather_pgms(self):
        """
        Gather pgms by getting components for each imt.

        Returns:
            dictionary: Dictionary of pgms.

        Notes:
            Assumes generate_oscillators has already been called for
            this class instance.
        """
        pgm_dict = {}
        for oscillator in self.oscillators:
            stream = self.oscillators[oscillator]
            if oscillator == 'PGA':
                pga = calculate_pga(stream, self.components)
                pgm_dict[oscillator] = pga
            elif oscillator == 'PGV':
                pgv = calculate_pgv(stream, self.components)
                pgm_dict[oscillator] = pgv
            elif oscillator.startswith('SA'):
                sa = calculate_sa(stream, self.components)
                pgm_dict[oscillator] = sa
        return pgm_dict

    def generate_oscillators(self):
        """
        Create dictionary of requested imt and its coinciding oscillators.

        Returns:
            dictionary: dictionary of oscillators for each imt.
        """
        oscillator_dict = OrderedDict()
        for imt in self.imts:
            stream = self.stream.copy()
            if imt.upper() == 'PGA':
                oscillator = self._get_acceleration(stream)
                oscillator_dict['PGA'] = oscillator
            elif imt.upper() == 'PGV':
                oscillator = self._get_velocity(stream)
                oscillator_dict['PGV'] = oscillator
            elif imt.upper().startswith('SA'):
                try:
                    period = float(re.search('\d+\.*\d*', imt).group())
                    oscillator = self._get_spectral(period,
                                                    stream,
                                                    damping=self.damping)
                    oscillator_dict[imt.upper()] = oscillator
                except Exception:
                    fmt = "Invalid period for imt: %r. Skipping..."
                    warnings.warn(fmt % (imt), Warning)
            else:
                fmt = "Invalid imt: %r. Skipping..."
                warnings.warn(fmt % (imt), Warning)
        return oscillator_dict

    def _get_acceleration(self, stream):
        """
        Returns a stream of acceleration with units of %%g.

        Args:
            stream (obspy.core.stream.Stream): Strong motion timeseries
                for one station.

        Returns:
            obpsy.core.stream.Stream: stream of acceleration.
        """
        accel_stream = Stream()
        for trace in stream:
            accel_trace = trace.copy()
            accel_trace.data = trace.data * GAL_TO_PCTG
            accel_trace.stats['units'] = '%%g'
            accel_stream.append(accel_trace)
        return accel_stream

    def _get_spectral(self, period, stream, damping):
        """
        Returns a stream of spectral response with units of %%g.

        Args:
            period (float): Period for spectral response.
            stream (obspy.core.stream.Stream): Strong motion timeseries
                for one station.
            damping (float): Damping of oscillator.

        Returns:
            obpsy.core.stream.Stream: stream of spectral response.
        """
        T = period
        freq = 1.0 / T
        omega = (2 * 3.14159 * freq) ** 2
        paz_sa = corn_freq_2_paz(freq, damp=damping)
        paz_sa['sensitivity'] = omega
        paz_sa['zeros'] = []
        spect_stream = Stream()
        for trace in stream:
            samp_rate = trace.stats['sampling_rate']
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                dd = simulate_seismometer(trace.data, samp_rate,
                                          paz_remove=None,
                                          paz_simulate=paz_sa,
                                          taper=True,
                                          simulate_sensitivity=True,
                                          taper_fraction=0.05)

            period_str = 'T' + '{:04.2f}'.format(T)
            stats_out = trace.stats.copy()
            stats_out['period'] = period_str
            self.period_str = period_str
            spect_trace = Trace(dd, stats_out)
            spect_trace.data = spect_trace.data * GAL_TO_PCTG
            spect_trace.stats['units'] = '%%g'
            spect_stream.append(spect_trace)
        return spect_stream

    def _get_velocity(self, stream):
        """
        Returns a stream of velocity with units of cm/s.

        Args:
            stream (obspy.core.stream.Stream): Strong motion timeseries
                for one station.

        Returns:
            obpsy.core.stream.Stream: stream of velocity.
        """
        veloc_stream = Stream()
        for trace in stream:
            veloc_trace = trace.copy()
            veloc_trace.integrate()
            veloc_trace.stats['units'] = 'cm/s'
            veloc_stream.append(veloc_trace)
        return veloc_stream
