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
    """Returns a panda of county seat` data

    Parameters
    ----------
    file : path
        The file path and name to the csv containing the county seat data

    Returns
    -------
    panda
        A panda of county seat information
    """
    counties = pd.read_csv(file, header=0)

    return county_seats

tmp = getcounties('../data/counties.csv')
print(tmp[0:5])

tmp = getcounties('../data/county-seats.csv')
print(tmp[0:5])
