
from __future__ import absolute_import

import googlemaps
import numpy as np
import os
import pandas as pd
from utils import _get

_POINTS_COL_NAMES_ = ['gid_county', 'name_county', 'lat_county',
                      'lon_county',
                      'state', 'cat_code', 'fips_code',
                      'gid_seat', 'name_seat', 'lat_seat', 'lon_seat',
                      'name_visit', 'lat_visit', 'lon_visit']


class TourRoute():
    '''
    Holds the tour route as a series of waypoints

    Usage::
        import tourroute
        tr = tourroute.TourRoute()
        tr.read_csv('../data/data_in.csv')
        slices = tr.slices(10)

    Class public methods:
        * add_points: Add points on the TourRoute
        * read_csv: Read in a TourRoute from a csv file
        * write_csv: Writes TourRoute to a csv file
        * get_points: Get points from the TourRoute
        * del_points: Delete points from the TourRoute
        * update_points: Update points on the TourRoute

        to dos / check:
        * update_visit_points: Updates the name_visit, lat_visit and lon_visit
            properties for the TourRoute. A visit point is the county seat if
            available, else the county
        * write_js: Writes TourRoute to a js file for use with Google Maps API
            use
        * slices: Slice a TourRoute into x slices of length y
        * flyingcrow_dist: Get the total TourRoute straight line distance
            between each point


    Class private methods:

    '''

    def __init__(self):
        '''

        '''
        self._points = pd.DataFrame(columns=_POINTS_COL_NAMES_)

    def add_points(self,
                   gid_county, name_county, lat_county, lon_county,
                   state, cat_code, fips_code,
                   gid_seat=None, name_seat=None, lat_seat=None, lon_seat=None,
                   name_visit=None, lat_visit=None, lon_visit=None):
        '''
        Add points to a TourRoute

        Args:
            gid_county (int): Geonames unique ID for the county
            name_county (str): County name
            lat_county (float): County latitude
            lon_county (float): County longitude
            state (str): County state; typically two letter abbreviation
            cat_code (str): Category code based on Geonames use. Format is
                CC.SS.AAA where CC is two letter country abbreviation, SS is
                two letter state abbreviation and AAA is three digit with
                leading zeros for the county number within the state e.g.
                US.NY.047 for Kings County in the state of New York, USA
            fips_code (int): Federal Information Processing Standards code for
                each county

        Optional:
            gid_seat (int): Geonames unique ID for the county seat. Defaults to
                ``None``.
            name_seat (str): County seat name. Defaults to ``None``.
            lat_seat (float): Seat latitude. Defaults to ``None``.
            lon_seat (float): Seat longitude. Defaults to ``None``.
            name_visit (str): Name of the visited point. Defaults to ``None``.
            lat_visit (float): Latitude of the visited point. Defaults to
                ``None``.
            lon_visit (float): Longitude of the visited point. Defaults to
                ``None``.

        Raises:
            Exception: AssertionError if any of the not None arguments are of
                different length to ``gid_county``
        '''

        new_points = pd.DataFrame()
        args = [gid_county, name_county, lat_county, lon_county,
                state, cat_code, fips_code,
                gid_seat, name_seat, lat_seat, lon_seat,
                name_visit, lat_visit, lon_visit]

        for i, arg in enumerate(args):
            if arg is None:
                new_points[_POINTS_COL_NAMES_[i]] = np.nan * len(new_points)
            else:
                # Check that the new data columns are of equal length
                if i == 0:
                    length_check = len(arg)

                error_msg = f'Argument ``{_POINTS_COL_NAMES_[i]}`` of ' \
                    + f'different length to ``{_POINTS_COL_NAMES_[0]}``'

                assert (len(arg) == length_check), error_msg
                new_points[_POINTS_COL_NAMES_[i]] = arg

        self._points = self._points.append(new_points)

    def read_csv(self, path,
                 col_map={'gid_county': 'gid_county',
                          'name_county': 'name_county',
                          'lat_county': 'lat_county',
                          'lon_county': 'lon_county',
                          'state': 'state',
                          'cat_code': 'cat_code',
                          'fips_code': 'fips_code'}):
        '''
        Args:
            path (handle): File path and name pointing to input data file
            col_map (dict): Mapping of ``add_points()`` argument names (the
                keys) to csv column names (the values). Defaults to minimum
                required columns for ``add_points()``.

        Notes:
            The input data file is expected to have `lat_visit` and `lon_visit`
            in the header, as the columns containing the latitude and longitude
            of each waypoint to visit, where each waypoint is a row
        '''

        keep_cols = list(col_map.values())
        df = pd.read_csv(path, header=0, usecols=keep_cols)
        dfl = []

        # Loop through list of possible column names
        # If name not found in the csv data `df`, then catch the error, and
        # append it as an empty data frame
        for col in _POINTS_COL_NAMES_:
            try:
                dfl.append(df[col_map[col]])
            except KeyError:
                dfl.append(pd.DataFrame(columns=[col]))  # Append as empty df

        # Use class method to add points
        # For optional arguments, check if it exists, if not then pass `None`
        # back to class method
        self.add_points(gid_county=dfl[0],
                        name_county=dfl[1],
                        lat_county=dfl[2],
                        lon_county=dfl[3],
                        state=dfl[4],
                        cat_code=dfl[5],
                        fips_code=dfl[6],
                        gid_seat=None if dfl[7].empty else dfl[7],
                        name_seat=None if dfl[8].empty else dfl[8],
                        lat_seat=None if dfl[9].empty else dfl[9],
                        lon_seat=None if dfl[10].empty else dfl[10],
                        name_visit=None if dfl[11].empty else dfl[11],
                        lat_visit=None if dfl[12].empty else dfl[12],
                        lon_visit=None if dfl[13].empty else dfl[13])

    def write_csv(self, path):
        '''
        Writes the TourRoute to the given path pointing to a csv file.

        Parameters:
            path (handle): A full path to a csv file e.g. ../data/data.csv.
                Will create dir and file if they do not exist

        '''

        # Create dir if it does not exist
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.mkdir(dir)

        self._points.to_csv(path, index=False)

    def get_points(self, locs, key='gid_county'):
        '''
        Gets point(s) from the TourRoute

        Parameters:
            locs ([list of ints]): List locations as either Geoname county ids
                or gpd.DataFrame integer row numbers
            key (str): Either ``'gid_county'`` or ``'ilocs'`` to determine
                reference type to get the desired rows. Defaults to
                ``'gid_county'``.

        Returns:
            pd.DataFrame of the desired points
        '''

        if key == 'gid_county':
            # Check that locs is a list for passing to df.isin()
            locs = locs if isinstance(locs, (list)) else [locs]
            df = self._points.loc[
                self._points.isin({'gid_county': locs}).gid_county]
        else:
            df = self._points.iloc[locs]

        return df

    def del_points(self, locs, key='gid_county'):
        '''
        Delete point(s) from the TourRoute

        Parameters:
            locs ([list of ints]): List locations as either Geoname county ids
                or gpd.DataFrame integer row numbers
            key (str): Either ``'gid_county'`` or ``'ilocs'`` to determine
                reference type to delete the desired rows. Defaults to
                ``'gid_county'``.

        '''

        if key == 'gid_county':
            # Check that locs is a list for passing to df.isin()
            locs = locs if isinstance(locs, (list)) else [locs]
            self._points.drop(
                self._points.loc[
                    self._points.isin({'gid_county': locs}).gid_county].index,
                axis=0, inplace=True)
        else:
            self._points.drop(index=self._points.iloc[locs].index,
                              inplace=True)

    def update_points(self, up_dict):
        '''
        Update point(s) from the TourRoute

        Parameters:
            up_dict (dict): Dictionary of points to be updated. Each key
                corresponds to a TourRoute column name, with a list of values
                to be updated for the respective key(s). Must contain the key
                ``gid_county`` to use as the index for updating the desired
                point(s) aka data frame row(s).

        Usage:
            updates = {'gid_county': [10, 20], 'name_county': ['foo', 'bar']}

        '''

        # Check that up_dict contains 'git_county' key

        # Get list of keys that is not 'git_county':: [upd_cols]

        # Update self._points
        # self._points.loc[self._points.isin({'gid_county': up_dict['gid_county'].values}).gid_county, [updcols]] = up_dict[[upd_cols]]

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

    def write_js(self, w, tour_name='optRoute'):
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

    def get_slice_drivedistdur(self, gmaps):
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
        wpts = self.waypoints
        if wpts is None:
            dir_result = gmaps.directions(origin=self.origin,
                                          destination=self.destination,
                                          mode="driving",
                                          units="metric")
        else:
            dir_result = gmaps.directions(origin=self.origin,
                                          destination=self.destination,
                                          waypoints=wpts,
                                          mode="driving",
                                          units="metric")

        if len(dir_result) == 0:
            print('No direction result found for')
            print(f'origin {self.origin} and '
                  + f'destination {self.destination}')
            return 0, 0, []

        if 'legs' in dir_result[0]:
            for leg in dir_result[0]['legs']:
                dist = leg['distance']['value']
                dur = leg['duration']['value']

        else:
            print('No `legs` found in dir_result[0] for')
            print(f'origin {self.origin} and '
                  + f'destination {self.destination}')
            return 0, 0, []

        return dist, dur


def get_drive_distdur(apikey, tour_slices):
    '''
    Gets the total tour distance and duration for the given list of
    TourSlices. Use slices as the Google Maps API can only handle a certain
    number of waypoints to decode. Hence, if dealing with many points, then
    slice up the tour into smaller pieces.

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
        dist, dur = tour_slice.get_slice_drivedistdur(gmaps)
        tdist += dist
        tdur += dur
        slicei += 1

    return tdist, tdur
