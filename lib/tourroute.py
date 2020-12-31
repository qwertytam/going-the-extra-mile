from __future__ import absolute_import

import googlemaps
import numpy as np
import os
from os import path as ospath
import pandas as pd
from utils import _get


class TourRoute():
    '''
    Holds the tour route as a series of waypoints from an input csv data
    file
    '''

    def __init__(self, path):
        '''
        Args:
            path (str): File path and name pointing to input data file

        Usage::

            import tourroute
            tr = tourroute.TourRoute('../data/data_in.csv')
            slices = tr.slices(10)

        Notes:
            The input data file is expected to have `lat_visit` and `lon_visit`
            in the header, as the columns containing the latitude and longitude
            of each waypoint to visit, where each waypoint is a row
        '''
        self.path = path
        self.length = None
        self.waypoints = None
        self._get_waypoints()

    def _get_waypoints(self):
        '''
        Get the waypoints from the given data path and file name. Expect
        to find `lat_visit` and `lon_visit` columns in the data file.e
        '''
        keep_cols = ['lat_visit', 'lon_visit']
        self.waypoints = pd.read_csv(self.path, header=0, usecols=keep_cols)
        self.length = len(self.waypoints)

    def slices(self, **kwargs):
        '''
        Returns a list of slices of length `lgth` (default=10). Each slice has
        a origin, destination and optional list of waypoints. Each point is a
        destination), with each waypoint adding incrementally to the length.
        tuple of `(lat, lon)` coordinates. Length is a minimum of two (origin,
        destination).

        Optional:
        Args:
            lgth (int): Length of each slice, default of 10, minimum of 2

        Returns:
            slice (list of dict): List of dicts where each dict has keys
                `origin`, `destination` and `waypoints`. List is ordered
                whereby each `origin` is the `destination` of the previous item
                in the list. `waypoints` is a list. Each point (`origin`,
                `destiatnion` or any of the items in the `waypoints` list) is a
                tuple of `('lat_visit', 'lon_visit')`.
        '''
        slice_len = max(2, _get(kwargs, 'lgth', default=10))  # Min length of 2
        slice_list = []
        inc = slice_len

        for i in range(0, self.length, inc):
            org = tuple(self.waypoints.iloc[i])
            dest = tuple(self.waypoints.iloc[min(self.length - 1, i + inc)])
            if slice_len > 2:
                wpts = list(
                    self.waypoints.iloc[(i+1):min(self.length-2, i+inc-1)
                                        ].itertuples(index=False,
                                                     name=None))
            slice_list.append(TourSlice(org, dest, wpts))

        return slice_list


class TourSlice():
    '''
    Holds a slice of the tour, with an origin, destination, and set of optional
    waypoints
    '''

    def __init__(self, origin, destination, waypoints=None):
        '''
        Args:
            origin (tuple): Latitude and longitude tuple of the origin
            destination (tuple): Latitude and longitude tuple of the
                destination
            waypoints (list of tuples): Optional list of latitude and longitude
                tuples of waypoints in between the origin and destination

        Usage::

        '''
        self.origin = origin
        self.destination = destination
        self.waypoints = waypoints


def save_polylines(apikey, tour_slices, path, overwrite=True, verbose=False):
    '''
    Saves the encoded polylines for the given list of TourSlices in the
    given file path and name.

    Args:
        apikey (str): Google API key to use for the Google Directions
            service
        tour_slices (list of TourSlice): A list of TourSlices, where each
            slice contains latitude and longitude coordinate tuples for an
            origin, destination and an (optional) list of waypoints
        overwrite (bool): If given path should be overwritten
        verbose (bool): Print diagnostic information

    Returns:
        dist (numeric): Total distance of the tour_slices in metres
        duration (numeric): Total duration taken to drive the tour_slice in
            seconds
    '''

    slicei = 0
    tdist = 0
    tdur = 0
    gmaps = googlemaps.Client(key=apikey)
    path_noresult = path + '_norslt.csv'

    if overwrite & ospath.exists(path):
        os.remove(path)

    if overwrite & ospath.exists(path_noresult):
        os.remove(path_noresult)

    for tour_slice in tour_slices:
        dist, dur, plines = get_polylines(gmaps, tour_slice)
        tdist = tdist + dist
        tdur = tdur + dur
        slicei = slicei + 1
        plines = pd.DataFrame(plines)

        if len(plines) > 0:
            plines.to_csv(path, index=False, header=False, mode='a')

            if verbose:
                print(f'Completed slice {slicei:,} of {len(tour_slices):,}')
        else:
            nrslt = []
            nrslt.append(tour_slice.origin)
            nrslt.append(tour_slice.waypoints)
            nrslt.append(tour_slice.destination)
            nrslt = pd.DataFrame(nrslt)
            nrslt.to_csv(path_noresult, index=False, header=False, mode='a')

            if verbose:
                print(f'No result for slice {slicei:,} '
                      + f'of {len(tour_slices):,}')

    return tdist, tdur


def get_polylines(gmaps, tour_slice):
    '''
    Gets the encoded polylines for the given tour_slice

    Args:
        gmaps (googlemaps Client): An initiated Google Maps Client
        tour_slice (TourSlice): A tour slice that contains latitude and
            longitude coordinate tuples for an origin, destination and an
            (optional) list of waypoints

    Returns:
        dist (numeric): Distance of the tour_slice in metres
        duration (numeric): Duration taken to drive the tour_slice in
            seconds
    '''
    wpts = tour_slice.waypoints
    if wpts is None:
        dir_result = gmaps.directions(origin=tour_slice.origin,
                                      destination=tour_slice.destination,
                                      mode="driving",
                                      units="metric")
    else:
        dir_result = gmaps.directions(origin=tour_slice.origin,
                                      destination=tour_slice.destination,
                                      waypoints=wpts,
                                      mode="driving",
                                      units="metric")

    plines = []
    if len(dir_result) == 0:
        print('No direction result found for')
        print(f'origin {tour_slice.origin} and '
              + f'destination {tour_slice.destination}')
        return 0, 0, []

    if 'legs' in dir_result[0]:
        for leg in dir_result[0]['legs']:
            dist = leg['distance']['value']
            dur = leg['duration']['value']

            for step in leg['steps']:
                plines = np.append(plines,
                                   step['polyline']['points'])
    else:
        print('No `legs` found in dir_result[0] for')
        print(f'origin {tour_slice.origin} and '
              + f'destination {tour_slice.destination}')
        return 0, 0, []

    return dist, dur, plines
