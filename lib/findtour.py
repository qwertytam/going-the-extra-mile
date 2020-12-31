# -*- coding: utf-8 -*-
"""Finding the optimised tour

This module contains functions to generate the optimal tour route.

This file  contains the following functions:

    * find_tour - find the optimal using the Concorde algorithm

"""

from concorde.tsp import TSPSolver
from datetime import datetime

# Class for terminal output colours


class bcolours:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def find_tour(data, time_bound=-1, random_seed=42):
    '''
    Use the Concorde algorithim to find the optimal tour. Returns the optimised
    tour.

    Parameters:
        dir (str): Path to identify items to remove e.g. ../data/
        time_bound (int): Time bound in seconds (?) for Concorde algorithim
        random_seed (int): Random seed for Concorde algorithim

    Returns:
        data.frame : Data frame of the optimal tour

    '''

    # Local function variables
    # gid for starting in Kings County, NY (i.e. Brooklyn)
    # Will use this to rotate the tour so that the starting point is this gid
    start_gid = 6941775

    # Instantiate solver
    solver = TSPSolver.from_data(
        data.lat_visit,
        data.lon_visit,
        norm="GEO"
    )

    # Find tour
    t = datetime.now()
    tour_data = solver.solve(time_bound=time_bound, verbose=False,
                             random_seed=random_seed)
    print(f'\n\n{"~"*80}\n')
    print(f'Tour found in {(datetime.now() - t)}')
    print(f'{bcolours.OKGREEN}Solver was successful{bcolours.ENDC}'
          if tour_data.success else
          f'{bcolours.FAIL}Solver was NOT successful{bcolours.ENDC}')

    # Rotate tour so that starting point is first
    tour_route = tour_data.tour
    while data.gid_county.iloc[tour_route[0]] != start_gid:
        tour_route = np.append(tour_route[1:], tour_route[:1])

    # Return the tour route in the optimised order
    data_out = data.iloc[tour_route]
    return data_out
