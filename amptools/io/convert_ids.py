#!/usr/bin/env python3

import requests

def convert_ids(source_id, source_catalog, out_catalog, collect_dloc=1.5,
                collect_dtime=60, misfit_dloc=105, misfit_dtime=13, misfit_dmag=0.8,
                preferred_only=None, include_info=None, return_json=None):

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
