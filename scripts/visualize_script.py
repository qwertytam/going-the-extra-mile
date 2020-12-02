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
"""

import os.path
import pandas as pd
import importlib.util

spec = importlib.util.spec_from_file_location("data", "../lib/visualize.py")
viz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(viz)

# Define global variables
header_names = ['gid_county', 'name_county', 'lat_county', 'lon_county',
                'state', 'cat_code', 'gid_seat', 'name_seat', 'lat_seat',
                'lon_seat', 'fips_code', 'name_visit', 'lat_visit',
                'lon_visit']
map_out_fnm = os.path.join('../out/', 'tour.html')

# Read in the tour data
data = pd.read_csv('../out/tour_30.csv', names=header_names, header=0)

# Plot the path as a series of straight lines and save to a html file
viz.plot_as_the_crow_flys(data, map_out_fnm)
