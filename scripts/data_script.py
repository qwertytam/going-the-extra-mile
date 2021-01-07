"""Tour Data Gathering & Finding

This script downloads, cleans and gathers county and seat data from Geonames,
then finds the optimal route using the Concorde algorithim. The Geonames data
is saved as a .csv file in the data folder. The script will overwrite currently
exisiting .csv files with the same name (see below) in the data folder. The
tour is saved in the out folder, with same caveats on overwriting etc.

The csv file seats_and_counties.csv contains the following columns: county or
    seat name, latitude, longitude, state, and geoname database id

By default each row is a county. However, where there is a county seat
identified, then each relevant row is a set, with the corresponding county row
removed from the data set.

This file makes use of the functions in the data.py module within this package.

This specific project is set up to visit every county and equivalent in the
continental US. Visit is defined as visiting the county seat, and if no
county seat exists, then the county location as given by geonames.

TO DO:
    * Make use of TourRoute class

"""


from lib import datagather as datag
from lib import tourroute as tr
from lib import findtour as ftour
import os.path
# import sys
# import importlib.util


class bcolours:  # Class for terminal output colours
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


print(f'\n\n{"~"*80}\n')
print(f'{"<"*5}{"-"*5}{" "*22}{bcolours.OKGREEN}'
      + f'Script starting{bcolours.ENDC}{" "*23}{"-"*5}{">"*5}\n\n')

# # Import custom modules
# # Data gatherer
# data_spec = importlib.util.spec_from_file_location("data",
#                                                    "../lib/datagather.py")
# datag = importlib.util.module_from_spec(data_spec)
# data_spec.loader.exec_module(datag)

# # Optimal tour finder
# ftour_spec = importlib.util.spec_from_file_location("data",
#                                                     "../lib/findtour.py")
# ftour = importlib.util.module_from_spec(ftour_spec)
# ftour_spec.loader.exec_module(ftour)

# # TourRoute class
# tr_spec = importlib.util.spec_from_file_location("data",
#                                                  "../lib/tourroute.py")
# troute = importlib.util.module_from_spec(tr_spec)
# tr_spec.loader.exec_module(troute)

# Get and wrangle the data
data_in_dir = './data'

# Geonames data
geonames_url = 'https://download.geonames.org/export/dump/US.zip'
geonames_data_path = os.path.join(data_in_dir, 'geonames_data.csv')
geonames_data = datag.dl_county_data(geonames_url, geonames_data_path)

# FIPS data
fips_url = 'https://raw.githubusercontent.com/python-visualization/folium/' + \
    'master/examples/data/us_county_data.csv'
fips_path = os.path.join(data_in_dir, 'fips_codes.csv')
fips_data = datag.dl_fips_codes(fips_url, fips_path)

# Merge/prep the Geonames and FIPs data
visit_data_path = os.path.join(data_in_dir, 'visit_data.csv')
# datag.prep_data(geonames_data, fips_data, visit_data_path)
visit_data = tr.TourRoute()
visit_data = datag.prep_data(geonames_data, fips_data)
# visit_data.write_csv(visit_data_path)

# Remove no longer required files
datag.remove_gndata(data_in_dir)

# Data quality check
visit_len = len(visit_data)  # How many rows do we have
# cc_nunique = visit_data.get_cols(['cat_code']).nunique()  # How many unique
cc_nunique = len(visit_data.get_uniques(['cat_code']))  # How many unique

counties_total = 3243  # ref Wikipedia for counties and equivalents
non_state_ncounties = {'AS': 5, 'GU': 1, 'MP': 4, 'PR': 78, 'UM': 9, 'VI': 3}
exp_ncounties = counties_total - sum(non_state_ncounties.values())

# 2021-01-07: Full data set has 3,142 counties (1 diff to expected of 3,143)
# with 0 duplicates
print(f'Full data set has {cc_nunique:,} counties'
      + f' ({exp_ncounties - cc_nunique:,} diff to expected of '
      + f'{exp_ncounties:,}) '
      + f'with {visit_len - cc_nunique:,} duplicates')

# How many county seats?
all_seats = visit_data.get_cols(['name_seat'])
# nseats = len(all_seats) - len(all_seats.loc[all_seats.isna().values])
nseats = len(all_seats) - len(all_seats.loc[all_seats.isna().name_seat])

# 2021-01-07: Full data set has 2,988 seats with 154 counties with no seats
print(f'Full data set has {nseats:,} seats '
      + f'with {visit_len - nseats:,} counties with no seats')

# Only interested in a tour of the continental 48 plus DC
keep_states = ['AL', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA',
               'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA',
               'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM',
               'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD',
               'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
# visit_data.drop(
#     visit_data.loc[~visit_data.isin({'state': keep_states}).state].index,
#     axis=0, inplace=True)

# Get the points to drop
drop_points = visit_data.get_points(
    ~visit_data.get_cols(['state']).isin({'state': keep_states}).values,
    key='ilocs')

# Now delete them
visit_data.del_points(drop_points.index, key='ilocs')

# 2021-01-07: For the continental 48 plus DC, looking to visit 3,108 counties
# with 120 counties with no seats
visit_len = len(visit_data)
nseats = len(all_seats) - len(all_seats.loc[all_seats.isna().values])
print('For the continental 48 plus DC, '
      + f'looking to visit {visit_len:,} counties '
      + f'with {visit_len - nseats:,} counties with no seats')

# # Run solver the save the optimised tour
opt_tour = ftour.find_tour(visit_data)
data_out_dir = '../out'
opt_tour_path_csv = os.path.join(data_out_dir, 'opt_tour.csv')
opt_tour.write_csv(opt_tour_path_csv)

opt_tour_path_js = os.path.join(data_out_dir, 'opt_tour.js')
opt_tour.write_js(opt_tour_path_js)

print(f'\n\n{bcolours.OKGREEN}{"<"*5}{"-"*5}{" "*22}Script completed'
      + f'{" "*22}{"-"*5}{">"*5}{bcolours.ENDC}')
print(f'\n{"~"*80}\n')
