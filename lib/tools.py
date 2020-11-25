'''
_______________|  tools.py :: Assorted tools for analysis of gold

CHANGE LOG  For LATEST version, see
https://github.com/qwertytam/going-the-extra-mile

2020-11-18  Initial version
'''
import pandas as pd
import numpy as np
import pylab as pl

import matplotlib.pyplot as plt
from matplotlib import collections as mc


def getcounties(file):
    """Returns a panda of county data

    Parameters
    ----------
    file : path
        The file path and name to the csv containing the county data

    Returns
    -------
    panda
        A panda of county information
    """
    counties = pd.read_csv(file, header=0)

    return counties


def getcounty_seats(file):
    """Returns a panda of county seat data

    Parameters
    ----------
    file : path
        The file path and name to the csv containing the county seat data

    Returns
    -------
    panda
        A panda of county seat information
    """
    seats = pd.read_csv(file, header=0)

    return seats


def join_counties_seats(counties, county_seats):
    """Returns a panda of county and county seat data

    Parameters
    ----------
    counties : panda
        The panda data frame of county information
    county_seats : panda
        The panda data frame of county seat information

    Returns
    -------
    panda
        A panda of joined county and county seat information
    """

    # Note produces NaN for counties with no seat, and ignores possible
    # duplicated county seat data
    cands = pd.merge(counties, county_seats, how='left',
                     on=['state', 'admin2_code'], suffixes=('_c', '_cs'))

    cands.columns = ['county_name', 'county_lat', 'county_lon', 'state',
                     'admin2_code', 'county_geoid', 'seat_name', 'seat_lat',
                     'seat_lon', 'seat_geoid']
    # cands.drop(['county_geoid', 'admin2_code', 'seat_geoid'],
    #                         axis=1, inplace=True)

    return cands


def visit_data(cands):
    """Returns a panda of county and county seat data with visit name, latitude
    and longitude coordinates

    Parameters
    ----------
    cands : panda
        The panda data frame of and county seat data

    Returns
    -------
    panda
        A panda of joined county and county seat information with visit
        name, latitude and longitude
    """

    cands['v_id'] = cands['county_geoid']
    cands['v_name'] = cands['county_name']
    cands['v_lat'] = cands['county_lat']
    cands['v_lon'] = cands['county_lon']

    cands.loc[cands['seat_geoid'].notna(), 'v_id'] = cands.loc[
        cands['seat_geoid'].notna(), 'seat_geoid']
    cands.loc[cands['seat_name'].notna(), 'v_name'] = cands.loc[
        cands['seat_name'].notna(), 'seat_name']
    cands.loc[cands['seat_lat'].notna(), 'v_lat'] = cands.loc[
        cands['seat_lat'].notna(), 'seat_lat']
    cands.loc[cands['seat_lon'].notna(), 'v_lon'] = cands.loc[
        cands['seat_lon'].notna(), 'seat_lon']

    return cands


def dict_data(cands):
    """Returns a dictionary of visit id as string, latitude and longitude
    coordinates

    Parameters
    ----------
    cands : panda
        The panda data frame with visit information

    Returns
    -------
    dict
        A dictionary of visit id as string, latitude and longitude coordinates
    """

    cands['v_id'] = cands['v_id'].astype(str)
    dict = cands.set_index(['v_id']).T.to_dict(orient='list')
    return dict


def rand_slice(cands, rand):
    """Returns a slice of the data frame from rand randomy chosen

    Parameters
    ----------
    cands : panda
        The panda data frame with visit information
    rand : integer
        The number of random items to return

    Returns
    -------
    panda
        The panda of length rand
    """
    rand_slice = cands.sample(n=rand)

    return rand_slice


def gather_tour(file, cands):
    """Returns a slice of the data frame from rand randomy chosen

    Parameters
    ----------
    cands : panda
        The panda data frame with visit information
    rand : integer
        The number of random items to return

    Returns
    -------
    panda
        The panda of length rand
    """
    tour_gids = pd.read_csv(file, header=0)
    tour_merge = pd.merge(tour_gids, cands, how='left',
                          left_on=['v_ids'], right_on=['v_id'])

    return tour_merge


def plot_path(tour):
    """Returns a slice of the data frame from rand randomy chosen

    Parameters
    ----------
    cands : panda
        The panda data frame with visit information
    rand : integer
        The number of random items to return

    Returns
    -------
    panda
        The panda of length rand
    """

    lines = [[(tour.v_lon[i], tour.v_lat[i]), (tour.v_lon[i+1], tour.v_lat[i+1])]
             for i in range(0, len(tour)-1)]
    lc = mc.LineCollection(lines, linewidths=2)
    fig, ax = pl.subplots(figsize=(10, 5))
    ax.set_aspect('equal')
    ax.add_collection(lc)
    ax.autoscale()
    plt.show()
