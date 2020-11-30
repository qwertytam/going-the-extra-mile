"""Geonames Data Gathering

This script downloads, cleans and gathers county and seat data from Geonames.
The data is saved as a .csv file in the data folder. The script will
overwrite currently exisiting .csv files with the same name (see below) in the
data folder.

The csv file seats_and_counties.csv contains the following columns: county or
    seat name, latitude, longitude, state, and geoname database id

By default each row is a county. However, where there is a county seat
identified, then each relevant row is a set, with the corresponding county row
removed from the data set.

This file makes use of the functions in the data.py module within this package.

This specific project is set up to visit every county and equivalent in the
continental US. Visit is defined as visiting the county seat, and if no
county seat exists, then the county location as given by geonames.

"""

import os.path
import importlib.util

spec = importlib.util.spec_from_file_location("data", "../lib/data.py")
gd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gd)
# foo.MyClass()
# import data as gd

# Define global variables
url = 'https://download.geonames.org/export/dump/US.zip'
# dir = 'E:/GitRepos/going-the-extra-mile/data'
dir = '/Users/TomMarshall/github/going-the-extra-mile/data/'
path = os.path.join(dir, 'seats_and_counties.csv')
seat_f_code = ['PPLA2']
county_f_code = ['ADM2']
codes = seat_f_code + county_f_code
id_cols = ['state', 'county']

# Download and filter the data
data = gd.dl_data(url, path, codes)

# Drop county seats Orange, CA and the Washington Street Courthouse Annex,
# as they are not county seats ref Wikipedia
drop_gids = [11497201, 5379513]
data.drop(data.loc[data.isin(drop_gids).gid].index, axis=0, inplace=True)

# # Oakley, KS is actually the county seat for Logan County,
# # i.e. for county 109 in KS
data.at[(data.state == 'KS') & (data.name == 'Oakley')
        & (data.f_code == seat_f_code[0]), 'county'] = 109

data = gd.filter_data(data, path, dflt_fcode=county_f_code,
                      keep_fcode=seat_f_code, check_id_cols=id_cols)

# Data quality check
adm2_n = len(data)  # How many rows do we have
adm2_uniq_n = len(data['state_county'].unique())  # How many duplicates?

counties_total = 3243  # ref Wikipedia for counties and equivalents
non_states = {'AS': 5, 'GU': 1, 'MP': 4, 'PR': 78, 'UM': 9, 'VI': 3}
exp_counties_n = counties_total - sum(non_states.values())

# 2020-11-30: Data has 3,142 counties (1 diff to expected 3,143) with 0
# duplicates
print(f'Data has {adm2_uniq_n:,} counties'
      + f' ({exp_counties_n - adm2_uniq_n:,} diff to expected of '
      + f'{exp_counties_n:,}) '
      + f'with {adm2_n - adm2_uniq_n:,} duplicates')

# How many county seats?
seat_n = len(data.loc[data.f_code == seat_f_code[0], 'state_county'])
seat_uniq_n = len(
    data.loc[data.f_code == seat_f_code[0], 'state_county'].unique())

# Any counties with multiple seats?
sc_n = data[
    data.f_code == seat_f_code[0]].groupby(['state_county'])['gid'].count()
sc_list = list(sc_n.loc[sc_n > 1].index.values)
sc_mults = data.loc[(data.isin({'state_county': sc_list}).f_code)
                    & (data.f_code == seat_f_code[0])]
counties_mult_seats_n = len(sc_mults.county.unique())

# 2020-11-30: 2,987 seats with 156 counties with no seats, 0 counties with
# multiple seats, and 0 duplicates
print(f'Data has {seat_uniq_n:,} '
      + f'seats with {exp_counties_n - seat_uniq_n:,} '
      + f'counties with no seats, {counties_mult_seats_n:,} '
      + 'counties with multiple seats'
      + f', and {adm2_n - adm2_uniq_n:,} duplicates')

# Only interested in a tour of the continental 48 plus DC
keep_states = ['AL', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA',
               'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA',
               'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM',
               'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD',
               'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
data.drop(data.loc[~data.isin({'state': keep_states}).state].index,
          axis=0, inplace=True)

# 2020-11-30: Looking to visit 3,108 counties
print(f'Looking to visit {len(data):,} counties')

gd.write_data(data, path)

gd.cleanup_geoname_data(dir)
print('#<<<<   Script completed   >>>>#')
