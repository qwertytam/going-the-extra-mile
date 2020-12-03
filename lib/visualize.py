# -*- coding: utf-8 -*-
"""Point-to-Point Tour Visualization Tools

A series of functions to display the optimal tour to visit a series of
latitude and longitude coordinates

Functions include:
    * plot_as_the_crow_flys: Plot a map with each point connected by a
        straight line i.e. as the crow flys
    * plot_driving: Plot of map with each point connected by driveable roads
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
    Initialises the map at the centre point with a zoom level

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
        my_map (folium map object): Map to plot route on

    Returns:
        map : folium map object of tour with plotted path
    '''

    points = []
    for row in data.itertuples():
        points.append(tuple([row.lat_visit, row.lon_visit]))

    # Define colours for our markers
    markers_n = 50
    palette = sns.color_palette(
        palette='RdYlGn',
        n_colors=markers_n)
    palette = [clrs.to_hex(p) for p in palette]

    # Add markers at start and end of tour
    name = f'Start tour at {data.name_visit.iloc[0]}, ' + \
        f'{data.state.iloc[0]}'
    folium.Marker(points[0], popup=str(name), icon=folium.Icon(
        color='red', icon_color=palette[0])).add_to(my_map)

    name = f'Finish tour at {data.name_visit.iloc[-1]}, ' \
        + f'{data.state.iloc[-1]} which is stop {len(data):,}'
    folium.Marker(
        points[-1], popup=str(name),
        icon=folium.Icon(color='green',
                         icon_color=palette[-1])).add_to(my_map)

    # And at stops in between
    stop_interval = round(len(data)/markers_n)
    for mkr in range(1, markers_n):
        stop_n = mkr * stop_interval
        name = f'{data.name_visit.iloc[stop_n]}, ' + \
            f'{data.state.iloc[stop_n]} is stop {stop_n:,}'
        icolor = palette[mkr]
        folium.Marker(points[stop_n], popup=str(name), icon=folium.Icon(
            color='cadetblue', icon_color=icolor)).add_to(my_map)

    # add lines
    folium.PolyLine(points, color='#363bdf',
                    weight=2, opacity=0.5).add_to(my_map)

    return my_map


def plot_coloured_counties(tour, my_map):
    '''
    Displays the given tour data on an open map using the folium library.
    The tour is diplayed as a series of inter-connected as the crow flys
    points i.e. straight lines between each point.

    Parameters:
        data (data.frame): A data frame with tour data
        my_map (folium map object): Map to plot colours on

    Returns:
        map : folium map object of tour with coloured counties
    '''
    url = 'https://raw.githubusercontent.com/python-visualization/folium/' + \
        'master/examples/data'
    county_geo = f'{url}/us_counties_20m_topo.json'

    colorscale = branca.colormap.LinearColormap(
        colors=('#fc8d59', '#ffffbf', '#91cf60'),
        vmin=0, vmax=len(tour)).to_step(n=3000)
    tour_series = pd.Series(data=tour.index, index=tour.fips_code)

    def style_function(feature):
        fips_id = int(feature['id'][-5:])
        order = tour_series.get(fips_id, None)

        if order is None:
            style_dict = {
                'fill': False,
                'weight': 0.0,
            }
        else:
            style_dict = {
                'color': 'black',
                'weight': 1,
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
