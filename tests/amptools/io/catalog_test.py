#!/usr/bin/env python

# third party imports
from lxml import etree

# local imports
from amptools.io.catalog import convert_ids, get_ingv_shakemap


def test_id_conversions():
    eventid = 'us10006g7d'
    target_ingv = '7073641'
    target_dict = {
        'EMSC': '525580',
        'UNID': '20160824_0000006',
        'ISC': '611462212',
        'INGV': target_ingv
    }

    new_id = convert_ids(eventid, 'USGS', 'INGV')
    assert new_id == target_ingv

    new_id = convert_ids(eventid, 'USGS', ['INGV'])
    assert new_id == target_ingv

    ids_dict = convert_ids(eventid, 'USGS', ['INGV', 'EMSC', 'UNID', 'ISC'])
    assert ids_dict == target_dict

    ids_dict = convert_ids(eventid, 'USGS', ['all'])
    assert ids_dict == target_dict

    ids_dict = convert_ids(eventid, 'USGS', 'all')
    assert ids_dict == target_dict

    ids_dict = convert_ids(target_ingv, 'INGV', 'all')
    del target_dict['INGV']
    target_dict['USGS'] = eventid
    assert ids_dict == target_dict

    try:
        convert_ids('invalid', 'USGS', 'all')
        success = True
    except Exception:
        success = False
    assert success == False

    try:
        convert_ids(eventid, 'invalid', 'all')
        success = True
    except Exception:
        success = False
    assert success == False

    try:
        convert_ids(eventid, 'USGS', 'unk')
        success = True
    except Exception:
        success = False
    assert success == False


def test_ingvfetch():
    eventid = '3011761'
    shakemap_xml = get_ingv_shakemap(eventid, catalog='ingv',
            output_format='event_dat', flag='0')
    assert isinstance(shakemap_xml, etree._Element)

    try:
        get_ingv_shakemap(eventid, catalog='INGV',
                output_format='event_dat', flag='1')
        success = True
    except Exception:
        success = False
    assert success == False

    try:
        get_ingv_shakemap(eventid, catalog='INGV',
                output_format='invalid', flag='0')
        success = True
    except Exception:
        success = False
    assert success == False

    try:
        get_ingv_shakemap(eventid, catalog='INVALID',
                output_format='event_dat', flag='0')
        success = True
    except Exception:
        success = False
    assert success == False


if __name__ == '__main__':
    test_id_conversions()
    test_ingvfetch()
