# -*- coding: utf-8 -*-
"""Data Gathering

This module contains functions to wrangle the data to visit the desired
locations. The functions in included here
will download, clean and gather the data from https://www.geonames.org/.

This file  contains the following functions:

    * dl_county_data - downloads the geoname data from the geonames server
    * _clean_countydata - cleans up known issues in the county data from
        geonames
    * dl_fips_codes - downloads FIPS codes for each county
    * _clean_fipsdata - cleans up known issues in the fips code data
    * prep_data - prepares the tour data for calculating the tour
    * write_data - writes given data to a csv file
    * remove_gndata - removes downloaded zip and txt files from geonames.org

"""

# import math
import numpy as np
import os.path
import pandas as pd
# from tourroute import TourRoute

from os import listdir, mkdir, remove
from re import search, sub
from requests import get
from zipfile import ZipFile

# Module global variables
_COUNTY_FCODE = 'ADM2'
_SEAT_FCODE = 'PPLA2'

# Class for terminal output colours


class bcolours:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def dl_county_data(url, path):
    '''
    Gathers the county and seat data from the given url. Adds cat_code
    (country.state.county) and some data corrections (by
    `calling _clean_countydata()`). Writes the corrected data to the the given
    path and also returns it.

    Parameters:
        url (str): A full url to a zip file e.g.
            https://www.data.org/data.zip
        path (str): A full path to a csv file e.g. ../data/data.csv. Will
            create dir and file if they do not exist

    Returns:
        data.frame : Data frame of downloaded data
    '''

    # Function local variables
    url_ext = '.zip'
    txt_ext = '.txt'
    # PPLA2 for county, ADM2 for county seat
    keep_fcodes = [_SEAT_FCODE, _COUNTY_FCODE]

    # csv header names and keep columns
    header_names = ['gid', 'name', 'asciiname', 'altnames', 'lat', 'lon',
                    'f_class', 'f_code', 'country', 'alt_country', 'state',
                    'county', 'admin3', 'admin4', 'popn', 'elev', 'dem', 'tz',
                    'mod_date']
    keep_cols = ['gid', 'name', 'lat', 'lon', 'f_class', 'f_code',
                 'country', 'state', 'county']

    # Specify dtype; warning is raised for country, state and county columns if
    # their type is not specified
    dyptes = {'gid': np.int32, 'name': str, 'lat': np.float64,
              'lon': np.float64, 'f_class': str, 'f_code': str, 'country': str,
              'state': str, 'county': str}
    # dyptes = {'country': str, 'state': str, 'county': 'Int64'}

    # Get the zip file name to be downloaded
    zip_fnm = search(r'(([0-9a-zA-Z])+\.zip)$', url)
    zip_fnm = zip_fnm.group(0)

    # Get the text file name we expect to find in the zip file
    txt_fnm = sub(url_ext, txt_ext, zip_fnm)

    # Create dir if it does not exist
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        mkdir(dir)
        print(f'Created dir {dir}')

    zip_path = os.path.join(dir, zip_fnm)
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

    # Read in county data from the extracted txt file
    data = pd.read_csv(txt_path, names=header_names, header=0, dtype=dyptes,
                       usecols=keep_cols, delimiter="\t", na_values=[-1])

    # Keep only the geoname feature code(s) of interest
    data.drop(data.loc[~data.isin({'f_code': keep_fcodes}).f_code].index,
              axis=0, inplace=True)

    data = _clean_countydata(data)

    # Add cat_code for reference and later use to identify county:seat
    # matchups
    data[['county']] = data[['county']].apply(pd.to_numeric)

    data['cat_code'] = data[['country', 'state', 'county']].apply(
        lambda x: (f'{x[0]}.{x[1]}.{x[2]:03d}'), axis=1)

    write_data(data, path)
    return data


def _clean_countydata(data):
    '''
    Cleans up known issues in the county data from geonames.org as of
    31 December 2020.

    Parameters:
        data (data.frame): Data frame of county data from geonames

    Returns:
        data.frame : Data frame of the corrected data

    ** TO DO: Add functions for update, add, remove. Then move the data below
        into csv files so that user edits the csv files, rather than source
        code
    '''

    # Name correction in data source
    data.loc[data['gid'] == 5465283, 'name'] = 'Dona Ana County'
    data.loc[data['gid'] == 5135484, 'name'] = 'Saint Lawrence County'

    # Add county seat for Inyo County, CA
    # The default county lat/lon coordinates
    new_data = pd.DataFrame({'gid': 9999999,
                             'name': 'Independence',
                             'lat': 36.802778,
                             'lon': -118.2,
                             'f_class': 'P',
                             'f_code': _SEAT_FCODE,
                             'country': 'US',
                             'state': 'CA',
                             'county': 27,
                             'cat_code': 'US.CA.027'})

    data = data.append(new_data)

    # Drop county seats Orange, CA and the Washington Street Courthouse Annex,
    # as they are not county seats ref Wikipedia
    drop_gids = [11497201, 5379513]
    data.drop(data.loc[data.isin(drop_gids).gid].index, axis=0, inplace=True)

    # # Oakley, KS is actually the county seat for Logan County,
    # # i.e. for county 109 in KS
    data.at[(data.state == 'KS') & (data.name == 'Oakley')
            & (data.f_code == _SEAT_FCODE), 'county'] = 109

    return data


def dl_fips_codes(url, path):
    '''
    Gathers the FIPS codes for each county from the given url. Performs some
    data corrections to add missing counties (by calling `_clean_fipsdata()`)
    and align the names with the names in the geonmaes data set. Writes the
    corrected data to the the given path and also returns it.

    Parameters:
        url (str): A full url to a zip file e.g.
            https://www.data.org/data.csv
        path (str): A full path to a csv file e.g. ../data/data.csv. Will
            create dir and file if they do not exist

    Returns:
        data.frame : Data frame of downloaded data
    '''

    # csv header names and keep columns
    header_names = ['FIPS_Code', 'State', 'Area_name',
                    'Civilian_labor_force_2011', 'Employed_2011',
                    'Unemployed_2011', 'Unemployment_rate_2011',
                    'Median_Household_Income_2011',
                    'Med_HH_Income_Percent_of_StateTotal_2011']
    keep_names = ['FIPS_Code', 'State', 'Area_name']

    # Specify dtype
    dyptes = {'FIPS_Code': 'Int64', 'State': str, 'Area_name': str}

    # Check url and path are correct form
    try:
        error_msg = f'.csv not found before or at end of url: {url}'
        assert (search(r'\.csv', url).span()[1] == len(url)), error_msg
    except AttributeError:
        print(f'.csv not found in url: {url}')
        raise
    else:
        print('url is correctly formed')

    try:
        error_msg = f'.csv not found before or at end of path: {path}'
        assert (search(r'\.csv', path).span()[1] == len(path)), error_msg
    except AttributeError:
        print(f'.csv not found in path: {path}')
        raise

    fips = pd.read_csv(url, na_values=[' '], names=header_names,
                       usecols=keep_names, header=0, dtype=dyptes)

    # Data correction and clean up
    fips = _clean_fipsdata(fips)

    # Update the column names to all lower case
    fips.columns = ['fips_code', 'state', 'name']
    write_data(fips, path)

    return fips


def _clean_fipsdata(data):
    '''
    Cleans up known issues in the fips code data from the github source as of
    31 December 2020.

    Parameters:
        data (data.frame): Data frame of fips code data from github source

    Returns:
        data.frame : Data frame of the corrected data

    ** TO DO: Add functions for update, add, remove. Then move the data below
        into csv files so that user edits the csv files, rather than source
        code
    '''

    # Replace strings to align with what is used in geonames data
    # St. to Saint
    pat = r'St\.'
    repl = 'Saint'
    data['Area_name'] = data.Area_name.str.replace(pat, repl)

    # Correct position of city in the county seat name
    # For case when name is one word before city
    pat = r'^(?P<name>\w+)(\scity)'
    def replfn(m): return ('City of ' + m.group('name'))
    data['Area_name'] = data.Area_name.str.replace(pat, replfn)

    # For case when name is two words before city
    pat = r'^(?P<name>\w+\s\w+)(\scity)'
    def replfn(m): return ('City of ' + m.group('name'))
    data['Area_name'] = data.Area_name.str.replace(pat, replfn)

    # Manual adds as not in data source
    data.loc[len(data.index)] = [2158, 'AK', 'Kusilvak Census Area']
    data.loc[len(data.index)] = [15005, 'HI', 'Kalawao County']
    data.loc[len(data.index)] = [46102, 'SD', 'Oglala Lakota County']

    # Manual corrections to align with geonames data
    data.loc[data['FIPS_Code'] == 2105, 'Area_name'] = \
        'Hoonah-Angoon Census Area'
    data.loc[data['FIPS_Code'] == 2198, 'Area_name'] = \
        'Prince of Wales-Hyder Census Area'
    data.loc[data['FIPS_Code'] == 2275, 'Area_name'] = \
        'City and Borough of Wrangell'
    data.loc[data['FIPS_Code'] == 6075, 'Area_name'] = \
        'City and County of San Francisco'
    data.loc[data['FIPS_Code'] == 11001, 'Area_name'] = 'Washington County'
    data.loc[data['FIPS_Code'] == 17099, 'Area_name'] = 'LaSalle County'
    data.loc[data['FIPS_Code'] == 28033, 'Area_name'] = 'De Soto County'
    data.loc[data['FIPS_Code'] == 29186, 'Area_name'] = \
        'Sainte Genevieve County'
    data.loc[data['FIPS_Code'] == 2195, 'Area_name'] = 'Petersburg Borough'

    return data


def prep_data(data, fips):
    '''
    Prepares data for finding tour with the following operations:
        * Adds column for FIPS code to match up with json data for mapping
        * Pivots data so that county and county seats are in separate columns
        * Adds a series of visit columns, where each entry is county
        information unless there is seat information in which case the seat
        information is used

    Parameters:
        data (data.frame): A data frame of geonames data that contains the
            county and county seat information
        fips (data.frame): A data frame of fips code data

    Returns:
        data.frame : Data frame of tour data

    ** TO DO:
        * Make use of the TourRoute class by:
            1) Move merged data into a new TourRoute object
            2) Use a TourRoute class method to create the visit data
            3) Use a TourRoute class method to write data to a csv file
    '''

    # Split the data and then remerge it, effectively pivoting it into wide
    # format
    counties = data.loc[data['f_code'] == _COUNTY_FCODE]
    seats = data.loc[data['f_code'] == _SEAT_FCODE]

    data = counties.merge(seats, how='left', copy=False,
                          suffixes=('_county', '_seat'), on='cat_code',
                          validate='1:1')

    # Drop unrequired and/or duplicated columns
    data.drop(['f_class_county', 'f_code_county', 'country_county',
               'county_county', 'f_class_seat', 'f_code_seat', 'country_seat',
               'state_seat', 'county_seat'], axis=1, inplace=True)

    # rename existing columns where appropiate
    data.rename(columns={'state_county': 'state'}, inplace=True)

    # Merge with the fips data
    data = data.merge(fips, how='left', copy=False,
                      suffixes=(None, '_fips'),
                      left_on=('name_county', 'state'),
                      right_on=('name', 'state'), validate='1:1')

    # Drop unrequired and/or duplicated columns
    data.drop(['name'], axis=1, inplace=True)

    # Return a TourRoute object
    # tr = TourRoute()
    print(data.columns)
    # tr.add_points(data)
    # return data


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
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        mkdir(dir)
        print(f'Created dir {dir}')

    print(f'Writing data to {path}')
    data.to_csv(path, index=False)
    print(f'Created and added data to {path}')


def remove_gndata(dir):
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
                item_pth = os.path.join(dir, item)
                remove(item_pth)
                print(f'Removed: {item_pth}')
