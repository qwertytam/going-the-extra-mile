# -*- coding: utf-8 -*-
from __future__ import print_function
from os.path import join
from simanneal import Annealer
from datetime import datetime
from collections import defaultdict

import csv
import math
import random
import tools as gem


def distance(a, b):
    """Calculates distance between two latitude-longitude coordinates."""
    R = 3963  # radius of Earth (miles)
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    return math.acos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(lon1-lon2)) * R


class TravellingSalesmanProblem(Annealer):

    """Test annealer with a travelling salesman problem.
    """

    # pass extra data (the distance matrix) into the constructor
    def __init__(self, state, distance_matrix):
        self.distance_matrix = distance_matrix
        super(TravellingSalesmanProblem, self).__init__(state)  # important!

    def move(self):
        """Swaps two cities in the route."""
        # no efficiency gain, just proof of concept
        # demonstrates returning the delta energy (optional)
        initial_energy = self.energy()

        a = random.randint(0, len(self.state) - 1)
        b = random.randint(0, len(self.state) - 1)
        self.state[a], self.state[b] = self.state[b], self.state[a]

        return self.energy() - initial_energy

    def energy(self):
        """Calculates the length of the route."""
        e = 0
        for i in range(len(self.state)):
            e += self.distance_matrix[self.state[i-1]][self.state[i]]
        return e


if __name__ == '__main__':

    # # latitude and longitude for the twenty largest U.S. cities

    data_dir = join('..', 'data')
    counties_csv_fnm = 'counties.csv'
    county_seat_csv_fnm = 'county-seats.csv'
    rand = 100

    counties = gem.getcounties(join(data_dir, counties_csv_fnm))
    seats = gem.getcounty_seats(join(data_dir, county_seat_csv_fnm))
    cands = gem.join_counties_seats(counties, seats)
    cands = gem.visit_data(cands)
    exc_states = ['AK', 'HI']
    cands_drop = cands[~cands.state.isin(exc_states)]
    # rand_slice = gem.rand_slice(cands_drop[['v_id', 'v_lat', 'v_lon']], rand)
    # cands_dict = gem.dict_data(rand_slice)
    cands_dict = gem.dict_data(cands_drop[['v_id', 'v_lat', 'v_lon']])
    cities = cands_dict

    # initial state, a randomly-ordered itinerary
    init_state = list(cities)
    random.shuffle(init_state)

    # create a distance matrix
    distance_matrix = defaultdict(dict)
    for ka, va in cities.items():
        for kb, vb in cities.items():
            distance_matrix[ka][kb] = 0.0 if kb == ka else distance(va, vb)

    tsp = TravellingSalesmanProblem(init_state, distance_matrix)
    auto_sch = tsp.auto(minutes=100)
    print('\n\nAuto schedule:')
    print(auto_sch)
    auto_sch['steps'] = 2000000
    auto_sch['updates'] = round(auto_sch['steps'] / 1000, 0)
    print('\n\nAuto schedule:')
    print(auto_sch)
    tsp.set_schedule(auto_sch)
    # since our state is just a list, slice is the fastest way to copy
    tsp.copy_strategy = "slice"
    state, e = tsp.anneal()

    # while state[0] != 'New York City':
    #     state = state[1:] + state[:1]  # rotate NYC to start

    for num in [1, 2, 3, 4]:
        print(num)

    print()
    print("%i mile route:" % e)
    # print(" -->  ".join(state))

    fin_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_fnm = format('anneal_out_{}.csv'.format(fin_time))
    outfile_fp = join(data_dir, out_fnm)

    with open(outfile_fp, 'w', encoding='utf8') as outcsv:
        print('Writing results to {}'.format(outfile_fp))
        writer = csv.writer(outcsv, lineterminator="\n")
        writer.writerow(['v_ids'])
        for row in state:
            row = [row]
            writer.writerow(row)

    print('Created and added data to {}'.format(outfile_fp))
    # file = 'anneal_out_20201119_170000.csv'
    # outfile_fp = join(data_dir, file)
    tour = gem.gather_tour(outfile_fp, cands)
    tour.drop(['county_name', 'county_lat', 'county_lon', 'state',
               'admin2_code', 'county_geoid', 'seat_name', 'seat_lat',
               'seat_lon', 'seat_geoid', 'v_id'], axis=1, inplace=True)
    gem.plot_path(tour)
