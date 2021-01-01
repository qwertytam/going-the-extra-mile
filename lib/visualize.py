# -*- coding: utf-8 -*-
"""Point-to-Point Tour Visualization Tools

A series of functions to display the optimal tour to visit a series of
latitude and longitude coordinates

Functions include:
    * init_map: Initiates a folium map object
    * plot_as_the_crow_flys: Plot a map with each point connected by a
        straight line i.e. as the crow flys
    * plot_markers: Displays the given tour data on an open map using markers
    * plot_coloured_counties:  Displays the given tour data on an open map
        using as a series of straight lines between each point
"""

from matplotlib import colors as clrs

import branca
import folium
import json
import pandas as pd
import requests
import seaborn as sns


def init_map(data):
    '''
    Initiates a folium map object centered at the average of the latitude and
    longitude position given in the data.

    Parameters:
        data (data.frame): A data frame with tour data

    Returns:
        map : folium map object of tour with plotted path
    '''
    points = []
    for row in data.itertuples():
        points.append(tuple([row.lat_visit, row.lon_visit]))

    # Find center for map display
    ave_lat = sum(p[0] for p in points)/len(points)
    ave_lon = sum(p[1] for p in points)/len(points)
    my_map = folium.Map(location=[ave_lat, ave_lon], zoom_start=4)

    return my_map


def plot_as_the_crow_flys(data, my_map):
    '''
    Displays the given tour data on an open map using the folium library.
    The tour is diplayed as a series of inter-connected as the crow flys
    points i.e. straight lines between each point.

    Parameters:
        data (data.frame): A data frame with tour data
        path (folium map object): A the map to add the path to

    Returns:
        map : folium map object of tour with plotted path
    '''

    points = []
    for row in data.itertuples():
        points.append(tuple([row.lat_visit, row.lon_visit]))

    # add lines
    folium.PolyLine(points, color="#364bea",
                    weight=2, opacity=0.7).add_to(my_map)

    return my_map


def plot_markers(data, my_map, n_markers):
    '''
    Displays the given tour data on an open map using markers.

    Parameters:
        data (data.frame): A data frame with tour data
        path (folium map object): A the map to add the path to
        n_markers (int): Number of markers to display

    Returns:
        map : folium map object of tour with plotted path
    '''

    points = []
    for row in data.itertuples():
        points.append(tuple([row.lat_visit, row.lon_visit]))

    # Define colours for our markers
    palette = sns.color_palette(palette="coolwarm", n_colors=n_markers)
    palette = [clrs.to_hex(p) for p in palette]

    # Add markers at start and end of tour
    name = f'Start tour at {data.name_visit.iloc[0]}, ' + \
        f'{data.state.iloc[0]}'
    folium.Marker(points[0], popup=str(name), icon=folium.Icon(
        color='blue', icon_color=palette[0])).add_to(my_map)

    name = f'Finish tour at {data.name_visit.iloc[-1]}, ' \
        + f'{data.state.iloc[-1]} which is stop {len(data):,}'
    folium.Marker(
        points[-1], popup=str(name),
        icon=folium.Icon(color='darkred',
                         icon_color=palette[-1])).add_to(my_map)

    # And at stops in between
    stop_interval = round(len(data)/n_markers)
    for mkr in range(1, n_markers):
        stop_n = mkr * stop_interval
        name = f'{data.name_visit.iloc[stop_n]}, ' + \
            f'{data.state.iloc[stop_n]} is stop {stop_n:,}'
        icolor = palette[mkr]
        folium.Marker(points[stop_n], popup=str(name), icon=folium.Icon(
            color='cadetblue', icon_color=icolor)).add_to(my_map)

    return my_map


def plot_circles(data, my_map, radius):
    '''
    Displays the given tour data on an open map using circles.

    Parameters:
        data (data.frame): A data frame with tour data
        path (folium map object): A the map to add the path to
        radius (Number): Radius of the circle in meters

    Returns:
        map : folium map object of tour with plotted path
    '''

    points = []
    for row in data.itertuples():
        points.append(tuple([row.lat_visit, row.lon_visit]))

    # Define colours for our circles
    palette = sns.color_palette(palette="Spectral", n_colors=len(data))
    palette = [clrs.to_hex(p) for p in palette]

    # # Add markers at start and end of tour
    name = f'Start tour at {data.name_visit.iloc[0]}, ' + \
        f'{data.state.iloc[0]}'
    folium.Marker(points[0], popup=str(name), icon=folium.Icon(
        color='darkred', icon_color=palette[0])).add_to(my_map)

    name = f'Finish tour at {data.name_visit.iloc[-1]}, ' \
        + f'{data.state.iloc[-1]} which is stop {len(data):,}'
    folium.Marker(
        points[-1], popup=str(name),
        icon=folium.Icon(color='darkpurple',
                         icon_color=palette[-1])).add_to(my_map)

    for idx, point in enumerate(points):
        folium.Circle(point, radius=radius, color=palette[idx],
                      weight=3, opacity=0.9).add_to(my_map)

    return my_map


def plot_coloured_counties(data, my_map):
    '''
    Displays the given tour data on an open map using the folium library.
    The tour is diplayed as a series of inter-connected as the crow flys
    points i.e. straight lines between each point.

    Parameters:
        data (data.frame): A data frame with tour data
        path (folium map object): A map to add the colours to

    Returns:
        map : folium map object of tour with coloured counties
    '''
    url = 'https://raw.githubusercontent.com/python-visualization/folium/' + \
        'master/examples/data'
    county_geo = f'{url}/us_counties_20m_topo.json'

    colorscale = branca.colormap.LinearColormap(
        colors=('#3a4cc0', '#a6c3fd', '#f6b69a', '#b30326'),
        vmin=0, vmax=len(data)).to_step(n=len(data))
    # colorscale = branca.colormap.linear.YlOrRd_09.scale(0, len(data))
    tour_series = pd.Series(data=data.index, index=data.fips_code)

    def style_function(feature):
        order = data_series.get(int(feature['id'][-5:]), None)

        if order is None:
            style_dict = {
                'fill': False,
                'weight': 0.0
            }
        else:
            style_dict = {
                'color': '#000',
                'weight': 1.0,
                'opacity': 0.3,
                'fillColor': colorscale(order),
                'fillOpacity': 0.7
            }

        return style_dict

    folium.TopoJson(
        json.loads(requests.get(county_geo).text),
        'objects.us_counties_20m',
        style_function=style_function
    ).add_to(my_map)

    return my_map
