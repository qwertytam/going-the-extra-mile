# -*- coding: utf-8 -*-
"""Finding the optimised tour

This module contains functions to generate the optimal tour route.

This file  contains the following functions:

    * find_tour - find the optimal using the Concorde algorithm

"""

import numpy as np

from concorde.tsp import TSPSolver
from datetime import datetime
from lib.tourroute import TourRoute


class bcolours:  # Class for terminal output colours
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def find_tour(tr, time_bound=60, random_seed=42, start_gid=6941775):
    '''
    Use the Concorde algorithim to find the optimal tour. Returns the optimised
    tour.

    Parameters:
        tr (TourRoute): TourRout to find a tour for
        time_bound (int): Time bound in seconds (?) for Concorde algorithim.
            Defaults to 60. For unbounded, use ``-1``
        random_seed (int): Random seed for Concorde algorithim. Defaults to 42.
        start_gid (int): Geonames county id to start the tour at. Defaults to
            6941775 (Kings County, NY)

    Returns:
        data.frame : Data frame of the optimal tour

    '''
    data = tr.get_cols(['lat_visit', 'lon_visit'])
    print(f'\n\ndata::\n{data}')

    # Instantiate solver
    solver = TSPSolver.from_data(
        data.lat_visit,
        data.lon_visit,
        norm="GEO"
    )

    # Find tour
    start_time = datetime.now()
    tour_data = solver.solve(time_bound=time_bound, verbose=False,
                             random_seed=random_seed)
    print(f'\n\n{"~"*80}\n')
    print(f'Tour found in {(datetime.now() - start_time)}')
    print(f'{bcolours.OKGREEN}Solver was successful{bcolours.ENDC}'
          if tour_data.success else
          f'{bcolours.FAIL}Solver was NOT successful{bcolours.ENDC}')

    print(f'\n\ntour_data::\n{tour_data}')
    print(f'\n\tour_data.tour::\n{tour_data.tour}')
    # Rotate tour so that starting point is first
    tour_route = tour_data.tour
    while data.gid_county.iloc[tour_route[0]] != start_gid:
        tour_route = np.append(tour_route[1:], tour_route[:1])

    # Return the tour route in the optimised order
    # data_out = data.iloc[tour_route]
    opt_tour = tr.get_points[locs = tour_route, key = 'ilocs']
    return opt_tour
