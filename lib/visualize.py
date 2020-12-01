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

import folium
import seaborn as sns


def plot_as_the_crow_flys(data, path):
    '''
    Displays the given tour data on an open map using the folium library.
    The tour is diplayed as a series of inter-connected as the crow flys
    points i.e. straight lines between each point.

    Parameters:
        data (data.frame): A data frame with tour data
        path (str): A full path to a html file e.g. ../out/map.html to save
            the map to
    '''

    points = []
    for row in data.itertuples():
        points.append(tuple([row.lat, row.lon]))

    # Find center for map display
    ave_lat = sum(p[0] for p in points)/len(points)
    ave_lon = sum(p[1] for p in points)/len(points)
    my_map = folium.Map(location=[ave_lat, ave_lon], zoom_start=4)

    # Define colours for our markers
    markers_n = 50
    palette = sns.color_palette(palette="coolwarm", n_colors=markers_n)
    palette = [clrs.to_hex(p) for p in palette]

    # Add markers at start and end of tour
    name = f'Start tour at {data.name.iloc[0]}, ' + \
        f'{data.state.iloc[0]}'
    folium.Marker(points[0], popup=str(name), icon=folium.Icon(
        color='blue', icon_color=palette[0])).add_to(my_map)

    name = f'Finish tour at {data.name.iloc[-1]}, ' \
        + f'{data.state.iloc[-1]} which is stop {len(data):,}'
    folium.Marker(
        points[-1], popup=str(name),
        icon=folium.Icon(color='darkred',
                         icon_color=palette[-1])).add_to(my_map)

    # And at stops in between
    stop_interval = round(len(data)/markers_n)
    for mkr in range(1, markers_n):
        stop_n = mkr * stop_interval
        name = f'{data.name.iloc[stop_n]}, ' + \
            f'{data.state.iloc[stop_n]} is stop {stop_n:,}'
        icolor = palette[mkr]
        folium.Marker(points[stop_n], popup=str(name), icon=folium.Icon(
            color='cadetblue', icon_color=icolor)).add_to(my_map)

    # add lines
    folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(my_map)

    # Display the map
    # my_map  # Commented out as not sure how to display map

    # Save map
    my_map.save(path)
