
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
