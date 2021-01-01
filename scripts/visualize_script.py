# -*- coding: utf-8 -*-
"""US County Map Tour Visualization

This script displays the result of finding the shortest path to visit all
contiental US counties and their equivalents (as defined by the US census
bureau).

The tour is read in from a csv file, then displayed and saved to html files:
    * As the crow flies i.e. a series of straight lines between each stop
    * As a driving map i.e. using roads between each stop

This specific project is set up to visit every county and equivalent in the
continental US. Visit is defined as visiting the county seat, and if no
county seat exists, then the county location as given by geonames.

To dos:
    * Make use of TourRoute class
"""

import os.path
import pandas as pd
import importlib.util

# Class for terminal output colours


class bcolours:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


print(f'\n\n{"~"*80}\n')
print(f'{"<"*5}{"-"*5}{" "*22}Script starting{" "*23}{"-"*5}{">"*5}\n\n')

spec = importlib.util.spec_from_file_location("data", "../lib/visualize.py")
viz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(viz)

# Define global variables
header_names = ['idx', 'gid_county', 'name_county', 'lat_county', 'lon_county',
                'state', 'cat_code', 'gid_seat', 'name_seat', 'lat_seat',
                'lon_seat', 'fips_code', 'name_visit', 'lat_visit',
                'lon_visit']
keep_cols = ['fips_code', 'name_visit', 'lat_visit', 'lon_visit']

map_out_fnm = os.path.join('../out/', 'tour.html')

# Read in the tour data.
tour = pd.read_csv('../out/tour.csv', names=header_names, header=0,
                   index_col=False)

# Plot the path as a series of straight lines and save to a html file
my_map = viz.init_map(tour)

# Other functions that may be used
# my_map = viz.plot_coloured_counties(tour, my_map)
# my_map = viz.plot_markers(tour, my_map, 50)

my_map = viz.plot_as_the_crow_flys(tour, my_map)
my_map = viz.plot_circles(tour, my_map, 1000)
my_map.save(map_out_fnm)

print(f'\n\n{bcolours.OKGREEN}{"<"*5}{"-"*5}{" "*22}Script completed'
      + f'{" "*22}{"-"*5}{">"*5}{bcolours.ENDC}')
print(f'\n{"~"*80}\n')
