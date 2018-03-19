[![Build Status](https://travis-ci.org/usgs/shakemap-amp-tools.svg?branch=master)](https://travis-ci.org/usgs/shakemap-amp-tools)

[![codecov](https://codecov.io/gh/mhearne-usgs/shakemap-amp-tools/branch/master/graph/badge.svg)](https://codecov.io/gh/mhearne-usgs/shakemap-amp-tools)


shakemap-amp-tools
=====

Fetch and process strong motion waveform/peak amplitude data.

# Introduction

shakemap-amp-tools is a project designed to provide a number of functions ancillary to the ShakeMap
project, mostly those having to do with finding and parsing strong ground motion data and converting
it into the XML data format used by ShakeMap.  This repository includes the following tools:

 * `amps2xml` Convert peak ground motions in Excel format to ShakeMap XML data structure.
 * `ftpfetch` Retrieve directories or files containing data from FTP url.
 * `sm2xml` Convert a directory of strong motion data files into ShakeMap xml.

# Installing

If you already have a miniconda or anaconda Python 3.X environment:

 - `conda install numpy`
 - `conda install pandas`
 - `conda install openpyxl` 
 - `conda install lxml`
 - `pip install git+https://github.com/mhearne-usgs/shakemap-amp-tools.git`

If you do not have anaconda or miniconda, but have Python 3.X installed with pip:
 - `pip install numpy`
 - `pip install pandas`
 - `pip install openpyxl` 
 - `pip install lxml`
 - `pip install git+https://github.com/mhearne-usgs/shakemap-amp-tools.git`

## Updating

 - `pip install --upgrade git+https://github.com/mhearne-usgs/shakemap-amp-tools.git`

# Tools

## sm2xml

This tool converts a directory of strong motion time series data from one of the following networks:

 - CWB: Taiwan Central Weather Bureau
 - GeoNet: New Zealand GNS
 - KNET: Japan K-NET data

## ftpfetch

This tool allows a user to fetch a file or directory of files from an FTP server.
If a username and password are required (KNET, for example) they can be provided
as command line options.

## amps2xml

This tool presumes that there are peak ground motion data available in *some* tabular form
that can easily be pasted into an Excel spreadsheet and manipulated manually.  These spreadsheets
must contain *generally* only tabular (rows/columns) data.

A "complete" peak ground motion table would look like this:

<table>
  <tr><th>reference</th><th>Jones and Smith, 2007. Journal of Seismology.</th></tr>
  <tr>
    <th>station</th>
    <th>lat</th>
    <th>longitude</th>
    <th>network</th>
    <th>location</th>
    <th>source</th>
    <th>distance</th>
    <th>intensity</th>
    <th colspan="5" align="center">hhe</th>
    <th colspan="5" align="center">hhn</th>
    <th colspan="5" align="center">hhz</th>
  </tr>
  <tr>
    <td> </td>
    <td> </td>
    <td> </td>
    <td> </td>
    <td> </td>
    <td> </td>
    <td> </td>
    <td> </td>

    <td>pga</td>
    <td>pgv</td>
    <td>psa03</td>
    <td>psa10</td>
    <td>psa30</td>

    <td>pga</td>
    <td>pgv</td>
    <td>psa03</td>
    <td>psa10</td>
    <td>psa30</td>

    <td>pga</td>
    <td>pgv</td>
    <td>psa03</td>
    <td>psa10</td>
    <td>psa30</td>
  </tr>

  <tr>  
    <td>ABC</td>
    <td>20.123</td>
    <td>-118.123</td>
    <td>MX</td>
    <td>Downtown Chiapas</td>
    <td>National Seismic Service</td>
    <td>120.1</td>
    <td>4.5</td>
    
    <td>0.5</td>
    <td>0.6</td>
    <td>0.7</td>
    <td>0.8</td>
    <td>0.9</td>

    <td>0.6</td>
    <td>0.7</td>
    <td>0.8</td>
    <td>0.9</td>
    <td>1.0</td>

    <td>0.5</td>
    <td>0.6</td>
    <td>0.7</td>
    <td>0.8</td>
    <td>0.9</td>
  </tr>
</table>

The reference section in the first row is mandatory, and should consist of a cell
in the first column with "reference" in it, and the cell in the second column containing
the reference string.

The required columns are:
 - station: Usually a short abbreviated code.
 - lat: Latitude of the station where data was collected.
 - lon: Longitude of the station where data was collected.
 - network: Usually a short code indicating the seismic network who collected the data.

In addition to these required columns, there must be additionally at least:
 - intensity: Modified Mercalli Intensity (MMI) at the station location.

AND/OR:
 - channel (more on this below), contaning at least one of the following:
     * pga: Peak Ground Acceleration, in units of %g.
     * pgv: Peak Ground Velocity, in units of cm/s.
     * psa03: Peak Spectral Acceleration at 0.3 seconds, in units of %g.
     * psa10: Peak Spectral Acceleration at 1.0 seconds, in units of %g.
     * psa30: Peak Spectral Acceleration at 3.0 seconds, in units of %g.

The channel columns can be one of three different naming schemes:
 - XXE, XXN, XXZ: Three channels named according to the scheme found at
                  http://www.fdsn.org/seed_manual/SEEDManual_V2.4_Appendix-A.pdf
                  where XXE/XXN are horizontal channels, and XXZ is the vertical channels.
 - H1, H2, Z: Three channels where the direction of the channel is not known,
              where H1/H2 are horizontal channels and Z is the vertical channel.
 - UNK: The "channel" to use when only summary peak ground motion values are known.

For the "XXE/XXN/XXZ" or "H1/H2/Z" naming schemes, at least one of the
horizontal channels must be included.

A minimum intensity only peak ground motion table would look like this:

<table>
  <tr><th>reference</th><th>Jones and Smith, 2007. Journal of Seismology.</th></tr>
  <tr>
    <td>station</td>
    <td>lat</td>
    <td>lon</td>
    <td>network</td>
    <td>intensity</td>
  </tr>
  <tr>  
    <td>ABC</td>
    <td>20.123</td>
    <td>-118.123</td>
    <td>MX</td>
    <td>4.5</td>
  </tr>
</table>

A minimum pga only peak ground motion table would look like this:

<table>
  <tr><th>reference</th><th>Jones and Smith, 2007. Journal of Seismology.</th></tr>
  <tr>
    <td>station</td>
    <td>lat</td>
    <td>lon</td>
    <td>network</td>
    <td>unk</td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>pga</td>
  </tr>
  <tr>  
    <td>ABC</td>
    <td>20.123</td>
    <td>-118.123</td>
    <td>MX</td>
    <td>0.5</td>
  </tr>
</table>

# Developer notes

The data file readers are modeled after obspy file readers, and have a standard interface.

Data file readers are located in `amptools/io/[format]/core.py`.

This core.py module should take the following form:

<pre>
def is_format(filename):
    # code to examine candidate file and determine if it is of the type specified.
    # return True if file is correct type, False otherwise.

def read_format(filename,**kwargs):
    # code to read file and return an obspy Stream object.
</pre>

The imports for this file should reside in the sm2xml program, and the package containing it
should be added to the setup.py script.


<!-- You will not be able to see this text. -->





  


