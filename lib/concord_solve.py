# -*- coding: utf-8 -*-
# %% [code]
# Required module installs
import seaborn as sns
import pylab as pl
import pandas as pd
import numpy as np
import folium
from os.path import join as pjoin
from matplotlib import colors as clrs
from matplotlib import collections as mc
from datetime import datetime
from concorde.tsp import TSPSolver
!pip install git+https: // github.com/jvkersch/pyconcorde.git

# %% [code]
# Module imports


# %% [code]
# Read in the data
input_dir = pjoin('..', 'input/geonames-us-data')
gdata_fnm = 'US.txt'

path = pjoin(input_dir, gdata_fnm)
gnames = ['gid', 'name', 'asciiname', 'altnames', 'lat', 'long', 'f_class', 'f_code', 'ISO_country',
          'alt_country', 'state', 'county', 'admin3', 'admin4', 'popn', 'elev', 'dem', 'tz', 'mod_date']
gucols = ['gid', 'name', 'lat', 'long', 'f_class', 'f_code', 'ISO_country', 'state', 'county']

# Specify dtype for certain columns to avoid warning
gdypte = {'ISO_country': str, 'state': str, 'county': str}
gdata = pd.read_csv(path, names=gnames, header=0, dtype=gdypte, usecols=gucols, delimiter="\t")

# %% [code]
# Keep only the county (ADM2) and county seat (PPLA2) data
keep_fcode = ['ADM2', 'PPLA2']
gdata.drop(gdata.loc[~gdata.isin({'f_code': keep_fcode}).f_code].index, axis=0, inplace=True)

# %% [code]
# Combine state and county columns to give unique id
gdata['state_county'] = gdata.apply(lambda x: str(x.state) + ':' + str(x.county), axis=1)

# %% [code]
f_code_county = 'ADM2'  # geoname code for admin level 2 i.e. county
f_code_seat = 'PPLA2'  # geoname code for seat of admin level 2 administration i.e. county seat

# Drop county seats Orange, CA and the Washington Street Courthouse Annex, as they are not county seats
# ref Wikipedia
drop_gids = [11497201, 5379513]
gdata.drop(gdata.loc[gdata.isin(drop_gids).gid].index, axis=0, inplace=True)

# Oakley, KS is actually the county seat for Logan County, state_county = 'KS:109'
gdata.loc[(gdata.state == 'KS') & (gdata.name == 'Oakley') & (
    gdata.f_code == f_code_seat), 'state_county'] = 'KS:109'

# %% [code]
# Data quality check
# How many counties do we have
num_adm2 = len(gdata[gdata.f_code == f_code_county])

# Any duplicates?
uniq_state_county_ids = gdata.state_county[gdata.f_code == f_code_county].unique()
num_adm2_uniq = len(uniq_state_county_ids)

# 2020-11-23: Data has 3,142 counties (1 diff to expected 3,143) with 0 duplicates
counties_total = 3243  # ref Wikipedia for counties and equivalents
non_states = {'AS': 5, 'GU': 1, 'MP': 4, 'PR': 78, 'UM': 9, 'VI': 3}
exp_counties_n = counties_total - sum(non_states.values())
print(f'Data has {num_adm2_uniq:,} counties ({exp_counties_n - num_adm2_uniq:,} ' +
      f'diff to expected {exp_counties_n:,}) with {num_adm2 - num_adm2_uniq:,} duplicates')

# %% [code]
# How many county seats
seat_ids = gdata[gdata.f_code == f_code_seat].state_county
num_seat = len(seat_ids)
num_seat_uniq = len(gdata.state_county[gdata.f_code == f_code_seat].unique())

# Any counties with multiple seats?
state_county_n = gdata[gdata.f_code == f_code_seat].groupby(['state_county'])['gid'].count()
state_county_list = list(state_county_n.loc[state_county_n > 1].index.values)
state_county_mults = gdata.loc[(gdata.isin({'state_county': state_county_list}).state_county) &
                               (gdata.f_code == f_code_seat)]
num_counties_mult_seats = len(state_county_mults.county.unique())

# 2020-11-23: 2,987 seats with 256 counties with no seats, 0 counties with multiple seats, and 0 duplicates
print(f'Data has {num_seat_uniq:,} seats with {unit_exp - num_seat_uniq:,} ' +
      f'counties with no seats, {num_counties_mult_seats:,} counties with multiple seats' +
      f', and {num_adm2 - num_adm2_uniq:,} duplicates')

# %% [code]
# Drop any county for which we have seat information
cities = gdata.drop(gdata.state_county[gdata.f_code == f_code_county].isin(
    seat_ids).index, axis=0, inplace=False)

# %% [code]
# Only interested in a tour of the continental 48 plus DC
keep_states = ['AL', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'ID', 'IL', 'IN', 'IA', 'KS',
               'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM',
               'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA',
               'WV', 'WI', 'WY']
cities.drop(cities.loc[~cities.isin({'state': keep_states}).state].index, axis=0, inplace=True)
# 2020-11-23: Looking to visit 2,975 counties
print(f'Looking to visit {len(cities):,} counties')

# %% [code]
# Instantiate solver
solver = TSPSolver.from_data(
    cities.lat,
    cities.long,
    norm="GEO"
)

# %% [code]
# Find tour
t = datetime.now()
tour_data = solver.solve(verbose=False, random_seed=42)
print(f'Tour found in {(datetime.now() - t)} and was solver successful? {tour_data.success}')

# %% [code]
# gid for starting in Brooklyn, NY
start_gid = 5110302

# Rotate tour so that starting point is first
tour_route = tour_data.tour
while cities.gid.iloc[tour_route[0]] != start_gid:
    tour_route = np.append(tour_route[1:], tour_route[:1])

# %% [code]
# Save tour to output file
cities.iloc[tour_route].to_csv('tour.csv')

# %% [code]
# Gather lat long for map display
points = []
for stop in tour_route:
    points.append(tuple([cities.lat.iloc[stop], cities.long.iloc[stop]]))

# Find center for map display
ave_lat = sum(p[0] for p in points)/len(points)
ave_lon = sum(p[1] for p in points)/len(points)
my_map = folium.Map(location=[ave_lat, ave_lon], zoom_start=4)

# %% [code]
# Define colours for our markers
markers_n = 50
palette = sns.color_palette(palette="coolwarm", n_colors=markers_n)
palette = [clrs.to_hex(p) for p in palette]

# %% [code]
# Add markers at start and end of tour
name = f'Start tour at {cities.name.iloc[tour_route[0]]}, {cities.state.iloc[tour_route[0]]}'
folium.Marker(points[0], popup=str(name), icon=folium.Icon(
    color='blue', icon_color=palette[0])).add_to(my_map)

name = f'Finish tour at {cities.name.iloc[tour_route[-1]]},, {cities.state.iloc[tour_route[-1]]} which is stop {len(cities):,}'
folium.Marker(points[-1], popup=str(name), icon=folium.Icon(color='darkred',
                                                            icon_color=palette[-1])).add_to(my_map)

# And at stops inbetween
city_interval = round(len(cities)/markers_n)
for mkr in range(1, markers_n):
    stop_n = mkr*city_interval
    name = f'{cities.name.iloc[tour_route[stop_n]]}, {cities.state.iloc[tour_route[stop_n]]} is stop {stop_n:,}'
    icolor = palette[mkr]
    folium.Marker(points[stop_n], popup=str(name), icon=folium.Icon(
        color='cadetblue', icon_color=icolor)).add_to(my_map)

# fadd lines
folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(my_map)

# Display the map
my_map

# %% [code]
# Save map
map_fnm = 'tour.html'
my_map.save(map_fnm)
