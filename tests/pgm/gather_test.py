#!/usr/bin/env python

# local imports
from pgm.gather import get_pgm_classes, group_imcs


def test_gather():
    imcs = get_pgm_classes('imc')
    imts = get_pgm_classes('imt')

    required_imcs = ['calculate_channels',
            'calculate_greater_of_two_horizontals',
            'calculate_gmrotd']
    required_imts = ['calculate_pga',
            'calculate_sa',
            'calculate_pgv']
    for imc in required_imcs:
        assert imc in imcs
    for imt in required_imts:
        assert imt in imts

    imcs = ['rotd0', 'roti10', 'gmrotd22', 'gmroti10',
            'rotd0invalid', 'roti10invalid', 'gmrotd22invalid',
            'gmroti10invalid', 'greater_of_two_horizontals']
    grouping = group_imcs(imcs)
    target_dict = {
        'rotd':[
            0.0
        ],
        'roti':[
            10.0
        ],
        'gmrotd':[
            22.0
        ],
        'gmroti':[
            10.0
        ],
        'greater_of_two_horizontals': ''
    }
    assert grouping == target_dict


if __name__ == '__main__':
    test_gather()
