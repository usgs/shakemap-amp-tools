#!/usr/bin/env python3
from amptools.io.convert_ids import convert_ids


def test_convert_id():

    ids = convert_ids('us20009ynd', 'USGS', 'INGV')
    assert ids == {'INGV': ['16399131']}
    try:
        ids = convert_ids('foo', 'USGS', 'INGV')
        success = True
    except ValueError:
        success = False
    assert success is False

    ids = convert_ids('us20009ynd', 'USGS', 'INGV', return_json=True)
    assert ids == [{'id': '16399131', 'm2': 3,
    'url': 'http://webservices.ingv.it/fdsnws/event/1/query?format=text&eventId=16399131',
    'misfit': 0.0701923235047, 'catalog': 'INGV'}]


if __name__ == '__main__':
    test_convert_id()
