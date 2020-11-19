'''
_______________|  tools.py :: Assorted tools for analysis of gold

CHANGE LOG  For LATEST version, see https://github.com/qwertytam/going-the-extra-milec
2020-11-18  Initial version
'''
import pandas as pd
import numpy as np

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
    county_seats = pd.read_csv(file, header=0)

    return county_seats


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
    county_and_seats = pd.merge(counties, county_seats, how='left',
                                on=['state', 'admin2_code'],
                                suffixes=('_c', '_cs'))

    county_and_seats.columns = ['county_name','county_lat', 'county_lon',
                                'state', 'admin2_code', 'county_geoid',
                                'county_seat_name', 'county_seat_lat',
                                'county_seat_lon', 'county_seat_geoid']
    county_and_seats.drop(['county_geoid', 'county_seat_geoid'],
                          axis=1, inplace=True)
    return county_and_seats


counties = getcounties('../data/counties.csv')
county_seats = getcounty_seats('../data/county-seats.csv')
county_and_seats = join_counties_seats(counties, county_seats)
county_and_seats.loc[county_and_seats['county_seat_lat'].notna(), 'county_lat'] = county_and_seats.loc[county_and_seats['county_seat_lat'].notna(), 'county_seat_lat']
county_and_seats.loc[county_and_seats['county_seat_lon'].notna(), 'county_lon'] = county_and_seats.loc[county_and_seats['county_seat_lon'].notna(), 'county_seat_lon']
print(county_and_seats)
