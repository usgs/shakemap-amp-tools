#!/usr/bin/env python3

import requests

def convert_ids(source_id, source_catalog, out_catalog, collect_dloc=1.5,
                collect_dtime=60, misfit_dloc=105, misfit_dtime=13, misfit_dmag=0.8,
                preferred_only=None, include_info=None, return_json=None):
    """
    This function will convert an event ID between the UNID, EMSC, INGV,
    USGS, and ISC catalogs.

    Args:
        source_id (str): Event ID from the source catalog.
        source_catalog (str): Source catalog (UNID, EMSC, INGV, USGS or ISC).
        out_catalog (str): Output cataog (UNID, EMSC, INGV, USGS, ISC, or all)
        collect_dloc (float): dloc parameter.
        collect_dtmie (float): dtime parameter.
        misfit_dloc (float): Misfit delta_loc parameter.
        misit_dtime (float): Misfit delta_time parameter.
        misfit_dmag (float): Misfit delta_mag parameter.
        preferred_only (str): Select only the first event by catalog if 'true'.
        include_info (str): Return info about the event if 'true'.

    Returns:
        dict: Returns a dictionary mapping catalogs to event IDS if return_json
              is False.
        list: Returns a list of the JSON if return_json is true.
    """

    arg_dict = locals()
    r = requests.get('http://www.seismicportal.eu/eventid/api/convert', params=arg_dict)

    if r.json() is None:
        raise ValueError('No matching event IDs were found.')

    if return_json is True:
        return r.json()
    else:
        catalog_id_dict = dict()
        for i in range(len(r.json())):
            if r.json()[i]['catalog'] in catalog_id_dict.keys():
                catalog_id_dict[r.json()[i]['catalog']].append(r.json()[i]['id'])
            else:
                catalog_id_dict[r.json()[i]['catalog']] = [r.json()[i]['id']]
        return catalog_id_dict
