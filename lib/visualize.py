# -*- coding: utf-8 -*-
"""...


"""

from matplotlib import colors as clrs

import folium
import pandas as pd
import seaborn as sns

# from matplotlib import collections as mc
# import pylab as pl
# from os import mkdir, remove
# from os.path import exists, join


def plot_path(data):

    # Gather lat lon for map display
    points = []
    print('--------\n')
    print(data)
    print(type(data))
    for tour_index in data:
        print(type(tour_index))
        print(tour_index)
        print('--------\n')
    #     points.append(tuple([lat, lon]))
    #
    # print(points)
    # # Find center for map display
    # ave_lat = sum(p[0] for p in points)/len(points)
    # ave_lon = sum(p[1] for p in points)/len(points)
    # my_map = folium.Map(location=[ave_lat, ave_lon], zoom_start=4)
    #
    # # Define colours for our markers
    # markers_n = 50
    # palette = sns.color_palette(palette="coolwarm", n_colors=markers_n)
    # palette = [clrs.to_hex(p) for p in palette]
    # # Add markers at start and end of tour
    # name = f'Start tour at {data.name.iloc[data[0]]}, '
    # + f'{data.state.iloc[data[0]]}'
    # folium.Marker(points[0], popup=str(name), icon=folium.Icon(
    #     color='blue', icon_color=palette[0])).add_to(my_map)
    #
    # name = f'Finish tour at {data.name.iloc[data[-1]]}, '
    # + f'{data.state.iloc[data[-1]]} which is stop {len(data):,}'
    # folium.Marker(
    #     points[-1], popup=str(name),
    #     icon=folium.Icon(color='darkred',
    #                      icon_color=palette[-1])).add_to(my_map)
    #
    # # And at stops inbetween
    # stop_interval = round(len(data)/markers_n)
    # for mkr in range(1, markers_n):
    #     stop_n = mkr * stop_interval
    #     name = f'{data.name.iloc[data[stop_n]]}, '
    #     + f'{data.state.iloc[data[stop_n]]} is stop {stop_n:,}'
    #     icolor = palette[mkr]
    #     folium.Marker(points[stop_n], popup=str(name), icon=folium.Icon(
    #         color='cadetblue', icon_color=icolor)).add_to(my_map)
    #
    # # add lines
    # folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(my_map)
    #
    # # Display the map
    # my_map
    #
    # # %% [code]
    # # Save map
    # map_fnm = 'tour.html'
    # my_map.save(map_fnm)


header_names = ['tour_index', 'gid', 'name', 'lat', 'lon', 'f_class', 'f_code',
                'country', 'state', 'county']
data = pd.read_csv('tour.csv', names=header_names, header=0)
plot_path(data)
