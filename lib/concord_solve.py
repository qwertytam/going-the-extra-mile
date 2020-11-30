# -*- coding: utf-8 -*-

from concorde.tsp import TSPSolver
from datetime import datetime
# from matplotlib import collections as mc
# from matplotlib import colors as clrs
import os.path
# import folium
import numpy as np
import pandas as pd
# import pylab as pl
# import seaborn as sns
# from os import mkdir, remove
# from os.path import exists, join

path = os.path.join('../data', 'seats_and_counties.csv')
cities = pd.read_csv(path, header=0)

# Instantiate solver
solver = TSPSolver.from_data(
    cities.lat,
    cities.lon,
    norm="GEO"
)

# Find tour
t = datetime.now()
tour_data = solver.solve(time_bound=-1, verbose=True, random_seed=42)
print(f'Tour found in {(datetime.now() - t)} and was solver successful?'
      + f' {tour_data.success}')

# gid for starting in Brooklyn, NY
start_gid = 5110302

# Rotate tour so that starting point is first
tour_route = tour_data.tour
while cities.gid.iloc[tour_route[0]] != start_gid:
    tour_route = np.append(tour_route[1:], tour_route[:1])

# Save tour to output file
cities.iloc[tour_route].to_csv('tour.csv')
