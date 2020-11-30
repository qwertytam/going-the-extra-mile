# -*- coding: utf-8 -*-
"""Data Gathering

This module contains functions to wrangle the data to visit the desired
locations. The functions in included here will download, clean and gather
the data from https://www.geonames.org/.

This file  contains the following functions:

    * dl_data - downloads the geoname data from the geonames server
    * filter_data - filters the data as required
    * write_data - writes given data to a csv file
    * cleanup_geoname_data - removes downloaded zip and txt files

"""

import pandas as pd

from os import listdir, mkdir, remove
from os.path import dirname, exists, join
from re import search, sub
from requests import get
from zipfile import ZipFile


def dl_data(url, path, geoname_feat_codes):
    '''
    Gathers the county data from the given url and stores it at the given path

    Parameters:
        url (str): A full url to a zip file e.g.
            https://www.data.org/data.zip
        path (str): A full path to a csv file e.g. ../data/data.csv. Will
            create dir and file if they do not exist
        geoname_feat_codes (list of str): List of geoname feature codes to
            keep in the output file e.g. ADM2 for administrative level 2

    Returns:
        data.frame : Data frame of downloaded data

    Raises:
        Exception: url does not point to a zip file
        Exception: path does not point to a csv file
    '''

    # Function local variables
    url_ext = '.zip'

    # Check url and path are correct form
    try:
        error_msg = f'.zip not found before or at end of url: {url}'
        assert (search(r'\.zip', url).span()[1] == len(url)), error_msg
    except AttributeError:
        print(f'.zip not found in url: {url}')
        raise
    else:
        print('url is correctly formed')

    try:
        error_msg = f'.csv not found before or at end of path: {path}'
        assert (search(r'\.csv', path).span()[1] == len(path)), error_msg
    except AttributeError:
        print(f'.csv not found in path: {path}')
        raise

    # Get the zip file name to be downloaded
    zip_fnm = search(r'(([0-9a-zA-Z])+\.zip)$', url)
    zip_fnm = zip_fnm.group(0)

    # Get the text file name we expect to find in the zip file
    txt_fnm = sub(url_ext, '.txt', zip_fnm)

    # Create dir if it does not exist
    dir = dirname(path)
    if not exists(dir):
        mkdir(dir)
        print(f'Created dir {dir}')

    zip_path = join(dir, zip_fnm)
    with open(zip_path, 'wb') as f:
        print(f'Downloading {url} to {zip_path}')
        response = get(url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                print(f'\r[{"="*done}{" "*(50-done)}] {done*2}%', end='\r')

    # Retrieve HTTP meta-data
    print(f'\nHTTP status {response.status_code}')
    print('Content type {}'.format(response.headers['content-type']))
    print(f'Enconding {response.encoding}')

    with ZipFile(zip_path, 'r') as zip_ref:
        print(f'Unzipping {zip_path}')
        txt_path = zip_ref.extract(txt_fnm, path=dir)
        zip_ref.close()
        print('Extracted {}'.format(txt_path))
    # txt_path = join(dir, txt_fnm)

    # Write the county data to csv file
    header_names = ['gid', 'name', 'asciiname', 'altnames', 'lat', 'lon',
                    'f_class', 'f_code', 'country', 'alt_country', 'state',
                    'county', 'admin3', 'admin4', 'popn', 'elev', 'dem', 'tz',
                    'mod_date']
    keep_cols = ['gid', 'name', 'lat', 'lon', 'f_class', 'f_code',
                 'country', 'state', 'county']

    # Specify dtype for certain columns to avoid warning; could do it for all
    # columns, but do not see the need yet
    dyptes = {'country': str, 'state': str, 'county': str}
    data = pd.read_csv(txt_path, names=header_names, header=0, dtype=dyptes,
                       usecols=keep_cols, delimiter="\t")

    # Keep only the geoname feature code(s) of interest
    data.drop(
        data.loc[~data.isin({'f_code': geoname_feat_codes}).f_code].index,
        axis=0, inplace=True)
    return data


def filter_data(data, path, dflt_fcode=None,
                keep_fcode=None, check_id_cols=None):
    '''
    Writes the given geoname data to the given path pointing to a csv file.
    Will prioritise geoname row data that have the keep_fcode feature codes
    over the dflt_fcode feature codes e.g. priortise county seat data over
    county data

    Parameters:
        data (data.frame): A data frame with geoname data
        path (str): A full path to a csv file e.g. ../data/data.csv. Will
            create dir and file if they do not exist
        dflt_fcode (list of str): List of geoname feature codes to
            keep if not dropped by keep_fcode e.g. ADM2 for administrative
            level 2
        keep_fcode (list of str): List of geoname feature codes to
            priortise over dflt_fcode e.g. PPLA2 for administrative level 2
            seats
        check_id_cols (list of str): The column names to join together and use
            to decide wether to keep dflt_fcode or keep_fcode rows e.g. could
            state codes and county codes columns to identify where there is
            information for a county and its seat present in data

    Returns:
        data.frame : Data frame of filtered data

    Raises:
        Exception: If only one of keep_fcode or check_id_cols is None
    '''

    # Check for the ambiguous case where the optional arguments are NOT all
    # None or all not None i.e. one or more of the arguments have been
    # specified but at least one of them is None
    if ((dflt_fcode is None) ^ (keep_fcode is None)) or \
            ((keep_fcode is None) ^ (check_id_cols is None)):
        emsg = 'Have specified one of dflt_fcode, keep_fcode or' + \
            ' check_id_cols whilist the other is None'
        raise Exception(emsg)

    if check_id_cols is None:
        id_col_name = None
    elif len(check_id_cols) == 1:
        id_col_name = check_id_cols
    else:
        # Include a spacer only in between each column name
        id_col_name = ''.join(
            map(lambda x: ''+x+'_', check_id_cols[:-1]))+str(check_id_cols[-1])
        print(f'New column name is {id_col_name}')

    if check_id_cols is None:
        id_col_name = None
    elif len(check_id_cols) > 1:
        # Include a spacer only in between each column
        data[id_col_name] = data[check_id_cols].apply(lambda x: ''.join(
            [str(x[c]) + '_' for c in x.index[:-1]])
            + str(x[x.index[-1]]), axis=1)

    # Drop any default row county for which we have keep information
    if keep_fcode is not None:
        keep_ids = data.loc[data.isin({'f_code': keep_fcode}).f_code,
                            id_col_name]
        keep_id_rows_bool = data[id_col_name].isin(keep_ids)
        dflt_rows_bool = data.isin({'f_code': dflt_fcode}).f_code
        data.drop(data.loc[dflt_rows_bool & keep_id_rows_bool].index,
                  axis=0, inplace=True)

    # Write the data to csv
    return data


def write_data(data, path):
    '''
    Writes the given data to the given path pointing to a csv file.

    Parameters:
        data (data.frame): A data frame of data
        path (str): A full path to a csv file e.g. ../data/data.csv. Will
            create dir and file if they do not exist

    Returns:
        data.frame : Data frame of filtered data

    Raises:
        Exception: path does not point to a csv file
    '''

    # Check if path is correct form
    try:
        error_msg = f'.csv not found before or at end of path: {path}'
        assert (search(r'\.csv', path).span()[1] == len(path)), error_msg
    except AttributeError:
        print(f'.csv not found in path: {path}')
        raise

    # Create dir if it does not exist
    dir = dirname(path)
    if not exists(dir):
        mkdir(dir)
        print(f'Created dir {dir}')

    print(f'Writing data to {path}')
    data.to_csv(path, index=False)
    print(f'Created and added data to {path}')


def cleanup_geoname_data(dir):
    '''
    Removes .zip and .txt files from the given dir

    Parameters:
        dir (str): Path to identify items to remove e.g. ../data/

    '''
    # Will remove .zip and .txt files
    rm_exts = ['.zip', '.txt']

    dir_items = listdir(dir)

    for ext in rm_exts:
        for item in dir_items:
            if item.endswith(ext):
                item_pth = join(dir, item)
                remove(item_pth)
                print(f'Removed: {item_pth}')
