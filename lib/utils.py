# -*- coding: utf-8 -*-
"""Utilities

This module contains utility type functions of use to the broader modulel.

This file  contains the following functions:

    * _get - Get the value of any of the provided keys for the given dictionary

"""

import numpy as np


def _get(dict, keys, default=None, get_key=False):
    '''
    Get the value of any of the provided keys.
    Note: Only use `dict.get()` if you have a single key and no optional
        parameters set, otherwise, prefer this function.
    Args:
        dict (dict): Dict to obtain the value from.
        keys (str or [str]): Keys of interest, in order of preference.

    Optional:
    Args:
        default: Value to return if none of the keys have a value. Defaults
            to None.
        get_key (bool): Whether or not to also return the key associated with
            the returned value. Defaults to False.

    Returns:
        any or (str, any): Value of the first valid key, or a tuple of the key
            and its value if ``get_key`` is True. If the default value is
            returned, the key is None.
    '''
    for key in (keys if isinstance(keys, (list, tuple)) else [keys]):
        value = dict.get(key)
        if value is not None:
            return value if not get_key else (key, value)
    return default if not get_key else (None, default)


def _format_jslocation(lat, lon):
    return f'location: {{ lat: {lat}, lng: {lon} }}'


def _format_jscounty(name, state, seat):
    return f'county: {{ name: \"{name}\", state: \"{state}\", ' \
        + 'seat: \"{seat}\" }}'


def haversine(lat1, lon1, lat2, lon2, to_radians=True, earth_radius=6371):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees or in radians)

    All (lat, lon) coordinates must have numeric dtypes and be of equal length.

    """
    if to_radians:
        lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])

    a = np.sin((lat2 - lat1) / 2.0) ** 2 + \
        np.cos(lat1) * np.cos(lat2) * \
        np.sin((lon2 - lon1)/2.0) ** 2

    return earth_radius * 2 * np.arcsin(np.sqrt(a))
