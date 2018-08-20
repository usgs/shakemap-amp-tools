
Status
=======
[![Build Status](https://travis-ci.org/usgs/shakemap-amp-tools.svg?branch=master)](https://travis-ci.org/usgs/shakemap-amp-tools)

[![codecov](https://codecov.io/gh/usgs/shakemap-amp-tools/branch/master/graph/badge.svg)](https://codecov.io/gh/usgs/shakemap-amp-tools)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/582cbceabb814eca9f708e37d6af9479)](https://www.codacy.com/app/mhearne-usgs/shakemap-amp-tools?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=usgs/shakemap-amp-tools&amp;utm_campaign=Badge_Grade)


shakemap-amp-tools
=====

Fetch, read, and process ground motion amplitude data.

# Introduction

shakemap-amp-tools is a project designed to provide a number of functions ancillary to the ShakeMap
project, mostly those having to do with finding and parsing strong ground motion data and converting
it into the XML data format used by ShakeMap.  This repository includes the following tools:

 * `amps2xml` Convert peak ground motions in Excel format to ShakeMap XML data structure.
 * `fdsnfetch` Retrieve data from an fdsn client (i.e. IRIS and ORFEUS).
 * `ftpfetch` Retrieve directories or files containing data from FTP url.
 * `ingvfetch` Retrieve ShakeMap xml data from the [INGV Strong Motions Web Service](http://webservices.ingv.it/swagger-ui/dist/?url=http%3A%2F%2Fwebservices.ingv.it%2Fingvws%2Fstrongmotion%2F1%2Fswagger.yml)
 * `sm2xml` Convert a directory of strong motion data files into ShakeMap xml.

# Installing

#### If you already have a miniconda or anaconda Python 3.5 environment:

Conda install:
- `conda install amptools`

Automated install:
- `git clone https://github.com/usgs/shakemap-amp-tools.git`
- `cd shakemap-amp-tools`
- `bash intall.sh`
- `conda activate amptools`

Manual install:
 - `conda install numpy`
 - `conda install pandas`
 - `conda install openpyxl`
 - `conda install lxml`
 - `pip install git+https://github.com/usgs/shakemap-amp-tools.git`


#### If you do not have anaconda or miniconda, but have Python 3.5 installed with pip:
 - `pip install numpy`
 - `pip install pandas`
 - `pip install openpyxl`
 - `pip install lxml`
 - `pip install git+https://github.com/usgs/shakemap-amp-tools.git`

## Updating

Updating conda install:
- `conda update amptools`

Updating automated install:
- `cd shakemap-amp-tools`
- `git pull --ff-only https://github.com/usgs/shakemap-amp-tools.git master`
- `bash install.sh`

Updating manually installed:
 - `pip install --upgrade git+https://github.com/usgs/shakemap-amp-tools.git`

# Tools


## sm2xml

This tool converts a directory of ground motion time series data into an xml file formatted for ShakeMap. The input file must be in a format supported by amptools:
- Cosmos
    - [Volume 1 and 2](https://strongmotioncenter.org/vdc/cosmos_format_1_20.pdf) are supported. No preprocessing applied.
- CWB
    - Provided by Taiwan Central Weather Bureau. No preprocessing applied.
- DMG
    - Synonymous with [CSMIP](ftp://ftp.consrv.ca.gov/pub/dmg/csmip/Formats/DMGformat85.pdf). No preprocessing applied.
- Geonet
    - Provided by New Zealand GNS. Currently [Volume 1 and 2](https://www.geonet.org.nz/data/supplementary/strong_motion_file_formats) are supported.
    - Data is converted from mm/s2 to cm/s2 when read in.

- KNET and KIKNET
    - Provided by Japan National Research Institute for Earth Science and Disaster
Resilience.
    - Time is converted from Japanese local time to UTC time (9 hour time shift).
    - A 15 second time delay (added by logger) is removed.
    - The data is detrended (linear and demean) as specified by [documentation](http://www.kyoshin.bosai.go.jp/kyoshin/man/knetform_en.html).
- Obspy
    - All obspy [supported formats](https://docs.obspy.org/packages/autogen/obspy.core.stream.read.html#supported-formats) are acceptable when accompanied by a JSON file containing metadata.
- SMC
    - Standard [U.S.G.S. format](https://escweb.wr.usgs.gov/nsmp-data/smcfmt.html) specified by the National Strong Motion Project. No preprocessing applied.
- USC
    - Provided by Los Angeles Basin Seismic Network, University of Southern California. No preprocessing applied.
    - [Volume 1 is supported](https://strongmotioncenter.org/vdc/USC_Vol1Format.txt). No preprocessing applied.

## fdsnfetch

This tool allows a user to fetch raw waveforms from an fdsn client.
Clipped waveforms are automatically removed. Each waveform is also demeaned and the instrument response is removed. Data is output as miniseed or sac, along with an accompanying metadata file for each station.

## ftpfetch

This tool allows a user to fetch a file or directory of files from an FTP server.
If a username and password are required (KNET, for example) they can be provided
as command line options.

## ingvfetch

This tool allows a user to fetch a ShakeMap xml file from the [INGV Strong Motions Web Service](http://webservices.ingv.it/swagger-ui/dist/?url=http%3A%2F%2Fwebservices.ingv.it%2Fingvws%2Fstrongmotion%2F1%2Fswagger.yml).
EventIDs from any of the following catalogs will be converted to an INGV eventID and will be used to retrieve a ShakeMap xml file if one is available:
- UNID
- EMSC
- USGS
- ISC

The INGV catalog is a combination of the CNT and ESM catalogs. With an INGV eventID, priority is given to ESM. In order to specify CNT or ESM, the catalog specific eventID and specifying the source catalog is required.


## amps2xml

This tool converts an excel file of peak ground motion data into an xml file formatted for use by ShakeMap. Excel spreadsheets
must contain only tabular (rows/columns) data.

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
 - channel (more on this below), containing at least one of the following:
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

**Links to example spreadsheets:**
- [Complete](https://github.com/usgs/shakemap-amp-tools/blob/master/tests/data/complete_pgm.xlsx)
- [Intensity only](https://github.com/usgs/shakemap-amp-tools/blob/master/tests/data/minimum_mmi.xlsx)
- [PGA only](https://github.com/usgs/shakemap-amp-tools/blob/master/tests/data/minimum_pga.xlsx)

# Developer notes

### Readers
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

### Intensity measurement types
In order to add an intensity measurement types (IMT) calculation, add a file with the type as the file name under pgm/imt/. The calculation should be called calculate_[TYPE], where [TYPE] matches the file name. The argument should always be *stream*. The second function should always be *imcs* (a list of requested components). All other functions in the file should be hidden by an underscore (example `def _get_horizontals(stream)`). The calculate function should return a dictionary of each component and the resulting values. Example:
<pre>
{
    'HN2': 81.234,
    'GMROTD0.0': 86.784,
    'GMROTD100.0': 96.446,
    'HN1': 99.249,
    'HNZ': 183.772,
    'GMROTD50.0': 92.177,
    'GREATER_OF_TWO_HORIZONTALS': 99.249
}
</pre>
StationSummary should be updated to handle the new IMT in `gather_pgms`.

### Intensity measurement components
In order to add an intensity measurement component (IMC) calculation, add a file with the component as the file name under pgm/imc/. The calculation should be called calculate_[COMPONENT], where [COMPONENT] matches the file name. The argument should always be *stream*. All other functions in the file should be hidden by an underscore (example `def _get_horizontals(stream)`). The calculate function should return a single value or a dictionary of each component and the resulting values. Imt calculations should be updated to handle a dictionary if one is returned. Otherwise, single values will automatically be handled.

Greater of two horizontals example:
99.249

Channels example:
<pre>
{
    'HN1': 99.249,
    'HN2': 81.234,
    'HNZ': 183.772
}
</pre>

GMRotD example:
<pre>
{
    0.0: 103.299,
    50.0: 119.925,
    100.0: 125.406
}
</pre>



#### For examples of the API see the [example notebooks](https://github.com/usgs/shakemap-amp-tools/tree/master/notebooks).
<!-- You will not be able to see this text. -->
