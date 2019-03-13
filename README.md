
Status
=======

Note: any general purpose ground motion processing functionality that was
in this repository is being moved to the
[groundmotion-processing](https://github.com/usgs/groundmotion-processing)
repository so that this repository will only conctain shakemap-specific
methods.


[![Build Status](https://travis-ci.org/usgs/shakemap-amp-tools.svg?branch=master)](https://travis-ci.org/usgs/shakemap-amp-tools)

[![codecov](https://codecov.io/gh/usgs/shakemap-amp-tools/branch/master/graph/badge.svg)](https://codecov.io/gh/usgs/shakemap-amp-tools)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/582cbceabb814eca9f708e37d6af9479)](https://www.codacy.com/app/mhearne-usgs/shakemap-amp-tools?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=usgs/shakemap-amp-tools&amp;utm_campaign=Badge_Grade)


shakemap-amp-tools
==================

Fetch, read, and process ground motion amplitude data.

# Introduction

shakemap-amp-tools is a project designed to provide a number of functions
ancillary to the ShakeMap project, mostly those having to do with finding
and parsing strong ground motion data and converting it into the XML data
format used by ShakeMap.  This repository includes the following tools:

 * `amps2xml` Convert peak ground motions in Excel format to ShakeMap XML
   data structure.
 * `sm2xml` Convert a directory of strong motion data files into ShakeMap xml.

# Installing

#### If you already have a miniconda or anaconda Python 3.5 environment:

For conda package:
- `conda install amptools`

Source code:
- `git clone https://github.com/usgs/shakemap-amp-tools.git`
- `cd shakemap-amp-tools`
- `bash intall.sh`
- `conda activate amptools`


# Tools

## sm2xml

This tool converts a directory of ground motion time series data into an xml
file formatted for ShakeMap. The input file must be in a format supported by
the[groundmotion-processing](https://github.com/usgs/groundmotion-processing).


## amps2xml

This tool converts an excel file of peak ground motion data into an xml file
formatted for use by ShakeMap. Excel spreadsheets must contain only tabular
(rows/columns) data.

A "complete" peak ground motion spreadsheet would look like this:

<table>
  <tr>
    <th>reference</th>
    <th>Mexican National Seismic Service report dated 2010-01-01</th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
    <th></th>
  </tr>
  <tr>
    <td>station</td>
    <td>NAME</td>
    <td>NETID</td>
    <td>SOURCE</td>
    <td>LAT</td>
    <td>LON</td>
    <td>ELEV</td>
    <td>DISTANCE</td>
    <td>INTENSITY</td>
    <td colspan="5">H1</td>
    <td colspan="5">H2</td>
    <td colspan="5">Z</td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>PGA</td>
    <td>PGV</td>
    <td>SA(0.3)</td>
    <td>SA(1.0)</td>
    <td>SA(3.0)</td>
    <td>PGA</td>
    <td>PGV</td>
    <td>SA(0.3)</td>
    <td>SA(1.0)</td>
    <td>SA(3.0)</td>
    <td>PGA</td>
    <td>PGV</td>
    <td>SA(0.3)</td>
    <td>SA(1.0)</td>
    <td>SA(3.0)</td>
  </tr>
  <tr>
    <td>ACAM</td>
    <td>Guanajuato</td>
    <td>MX</td>
    <td>National Seismic Service</td>
    <td>20.043186</td>
    <td>-100.716777</td>
    <td>5.1</td>
    <td>913.1</td>
    <td>0.72</td>
    <td>4.48</td>
    <td>1.31</td>
    <td>5.12</td>
    <td>7.74</td>
    <td>2.93</td>
    <td>4.928</td>
    <td>1.44</td>
    <td>5.632</td>
    <td>8.514</td>
    <td>3.223</td>
    <td>4.256</td>
    <td>1.24</td>
    <td>4.864</td>
    <td>7.353</td>
    <td>2.784</td>
  </tr>
</table>

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


#### Spreadsheet Requirements

The reference section in the first row is mandatory, and should consist of a
cell in the first column with "reference" in it, and the cell in the second
column containing the reference string.

The required columns are:
 - station: Usually a short abbreviated code.
 - lat: Latitude of the station where data was collected.
 - lon: Longitude of the station where data was collected.
 - network: Usually a short code indicating the seismic network who collected
   the data.

In addition to these required columns, there must be additionally at least:
 - intensity: Modified Mercalli Intensity (MMI) at the station location.

AND/OR:
 - channel (more on this below), containing at least one of the following:
     * pga: Peak Ground Acceleration, in units of %g.
     * pgv: Peak Ground Velocity, in units of cm/s.
     * psa03: Peak Spectral Acceleration at 0.3 seconds, in units of %g.
     * psa10: Peak Spectral Acceleration at 1.0 seconds, in units of %g.
     * psa30: Peak Spectral Acceleration at 3.0 seconds, in units of %g.

The channel columns can be one of three different naming schemes:
 - XXE, XXN, XXZ: Three channels named according to the scheme found at
   http://www.fdsn.org/seed_manual/SEEDManual_V2.4_Appendix-A.pdf
   where XXE/XXN are horizontal channels, and XXZ is the vertical
   channels.
 - H1, H2, Z: Three channels where the direction of the channel is not known,
   where H1/H2 are horizontal channels and Z is the vertical channel.
 - UNK: The "channel" to use when only summary peak ground motion values are
   known.

For the "XXE/XXN/XXZ" or "H1/H2/Z" naming schemes, at least one of the
horizontal channels must be included.

**Links to example spreadsheets:**
- [Complete](https://github.com/usgs/shakemap-amp-tools/blob/master/tests/data/complete_pgm.xlsx)
- [Intensity only](https://github.com/usgs/shakemap-amp-tools/blob/master/tests/data/minimum_mmi.xlsx)
- [PGA only](https://github.com/usgs/shakemap-amp-tools/blob/master/tests/data/minimum_pga.xlsx)

