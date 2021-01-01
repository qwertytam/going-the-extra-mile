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

        # '''
        # Args:
        #     lats ([float]): Latitudes for tour stop points
        #     lngs ([float]): Longitudes for tour stop points
        #     names ([strings]): County names for each tour stop point
        #     states ([strings]): County states for each tour stop point
        #     seats ([strings]): County seat names for each tour stop point
        # '''
        # self._points = [_format_tour_points(lat, lng, name, state, seat) for lat, lng, name, state, seat in zip(lats, lngs, names, states, seats)]
        

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

    def write_to_js(self, w, tour_name=optRoute):
        '''
        Write the TourRoute to a javascript file
        Args:
            w (_Writer): Writer used to write the TourRoute

        Optional:
            tour_name (string): Variable name to be used in the output file.
                Defaults to `optRoute`.
        '''
        w.write(f'var {tour_name} = [')
        w.indent()
        [w.write(f'{point}') for point in self._points]
        w.dedent()
        w.write('];')
        w.write()


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


def get_tour_distdur(apikey, tour_slices):
    '''
    Gets the total tour distance and duration for the given list of TourSlices.
    Use slices as the Google Maps API can only handle a certain number of
    waypoints to decode. Hence, if dealing with many points, then slice up the
    tour into smaller pieces.

    Args:
        apikey (str): Google API key to use for the Google Directions
            service
        tour_slices (list of TourSlice): A list of TourSlices, where each
            slice contains latitude and longitude coordinate tuples for an
            origin, destination and an (optional) list of waypoints

    Returns:
        dist (numeric): Total distance of the tour_slices in metres
        duration (numeric): Total duration taken to drive the tour_slice in
            seconds
    '''

    slicei = 0
    tdist = 0
    tdur = 0
    gmaps = googlemaps.Client(key=apikey)

    for tour_slice in tour_slices:
        dist, dur  = get_slice_distdur(gmaps, tour_slice)
        tdist += dist
        tdur += dur
        slicei++

    return tdist, tdur


def get_slice_distdur(gmaps, tour_slice):
    '''
    Get distance and duration for the given tour_slice

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

    if len(dir_result) == 0:
        print('No direction result found for')
        print(f'origin {tour_slice.origin} and '
              + f'destination {tour_slice.destination}')
        return 0, 0, []

    if 'legs' in dir_result[0]:
        for leg in dir_result[0]['legs']:
            dist = leg['distance']['value']
            dur = leg['duration']['value']

    else:
        print('No `legs` found in dir_result[0] for')
        print(f'origin {tour_slice.origin} and '
              + f'destination {tour_slice.destination}')
        return 0, 0, []

    return dist, dur
