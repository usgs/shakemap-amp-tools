#!/usr/bin/env python

import os.path
import numpy as np
from amptools.table import read_excel

def test_read_tables():
    homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
    datadir = os.path.join(homedir,'..','data')

    complete_file = os.path.join(datadir,'complete_pgm.xlsx')
    df_complete = read_excel(complete_file)
    np.testing.assert_almost_equal(df_complete['h1']['pga'].sum(),569.17)
        
    pgamin_file = os.path.join(datadir,'minimum_pga.xlsx')
    df_pgamin = read_excel(pgamin_file)
    np.testing.assert_almost_equal(df_pgamin['unk']['pga'].sum(),569.17)
    

    mmimin_file = os.path.join(datadir,'minimum_mmi.xlsx')
    df_mmimin = read_excel(mmimin_file)
    np.testing.assert_almost_equal(df_mmimin['intensity'].sum(),45.199872273516036)

    try:
        missing_file = os.path.join(datadir,'missing_columns.xlsx')
        read_excel(missing_file)
        assert 1==2
    except KeyError as ke:
        assert 1==1

    try:
        wrong_file = os.path.join(datadir,'wrong_channels.xlsx')
        read_excel(wrong_file)
        assert 1==2
    except KeyError as ke:
        assert 1==1

    try:
        nodata_file = os.path.join(datadir,'no_data.xlsx')
        read_excel(nodata_file)
        assert 1==2
    except KeyError as ke:
        assert 1==1

    try:
        emptyrow_file = os.path.join(datadir,'empty_row.xlsx')
        read_excel(emptyrow_file)
        assert 1==2
    except IndexError as ie:
        assert 1==1


    missing_data_file = os.path.join(datadir,'missing_rows.xlsx')
    df = read_excel(missing_data_file)
    assert np.isnan(df['h1']['psa03']['CHPA'])


if __name__ == '__main__':
    test_read_tables()
