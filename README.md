shakemap-amp-tools
=====

Fetch and process strong motion waveform/peak amplitude data.

# Introduction

shakemap-amp-tools is a project designed to provide a number of functions ancillary to the ShakeMap
project, mostly those having to do with finding and parsing strong ground motion data and converting
it into the XML data format used by ShakeMap.  This repository includes the following tools:

 * `amps2xml` Convert peak ground motions in Excel format to ShakeMap XML data structure.

# Tools

## amps2xml

This tool presumes that there are peak ground motion data available in *some* tabular form
that can easily be pasted into an Excel spreadsheet and manipulated manually.  These spreadsheets
must contain *generally* only tabular (rows/columns) data.

A "complete" peak ground motion table would look like this:

<table>
  <tr><td>reference</td><td>Jones and Smith, 2007. Journal of Seismology.</td></tr>
  <tr>
    <td>station</td>
    <td>latitude</td>
    <td>longitude</td>
    <td>network</td>
    <td>location</td>
    <td>source</td>
    <td>distance</td>
    <td>intensity</td>
    <td colspan="5" align="center">hhe</td>
    <td colspan="5" align="center">hhn</td>
    <td colspan="5" align="center">hhz</td>
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

The reference section in the first row is optional, but if present should consist of a cell
in the first column with "reference" in it, and the cell in the second column containing
the reference string.

The required columns are:
 - station: Usually a short abbreviated code.
 - latitude: Latitude of the station where data was collected.
 - longitude: Latitude of the station where data was collected.
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
  <tr>
    <td>station</td>
    <td>latitude</td>
    <td>longitude</td>
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
  <tr>
    <td>station</td>
    <td>latitude</td>
    <td>longitude</td>
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











  


