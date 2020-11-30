# -*- coding: utf-8 -*-
"""...


"""

# %% [code]
# Gather lat long for map display
points = []
for stop in tour_route:
    points.append(tuple([cities.lat.iloc[stop], cities.long.iloc[stop]]))

# Find center for map display
ave_lat = sum(p[0] for p in points)/len(points)
ave_lon = sum(p[1] for p in points)/len(points)
my_map = folium.Map(location=[ave_lat, ave_lon], zoom_start=4)

# %% [code]
# Define colours for our markers
markers_n = 50
palette = sns.color_palette(palette="coolwarm", n_colors=markers_n)
palette = [clrs.to_hex(p) for p in palette]

# %% [code]
# Add markers at start and end of tour
name = f'Start tour at {cities.name.iloc[tour_route[0]]}, {cities.state.iloc[tour_route[0]]}'
folium.Marker(points[0], popup=str(name), icon=folium.Icon(
    color='blue', icon_color=palette[0])).add_to(my_map)

name = f'Finish tour at {cities.name.iloc[tour_route[-1]]},, {cities.state.iloc[tour_route[-1]]} which is stop {len(cities):,}'
folium.Marker(points[-1], popup=str(name), icon=folium.Icon(color='darkred',
                                                            icon_color=palette[-1])).add_to(my_map)

# And at stops inbetween
city_interval = round(len(cities)/markers_n)
for mkr in range(1, markers_n):
    stop_n = mkr*city_interval
    name = f'{cities.name.iloc[tour_route[stop_n]]}, {cities.state.iloc[tour_route[stop_n]]} is stop {stop_n:,}'
    icolor = palette[mkr]
    folium.Marker(points[stop_n], popup=str(name), icon=folium.Icon(
        color='cadetblue', icon_color=icolor)).add_to(my_map)

# fadd lines
folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(my_map)

# Display the map
my_map

# %% [code]
# Save map
map_fnm = 'tour.html'
my_map.save(map_fnm)


def plot_path(tour):
    """Returns a slice of the data frame from rand randomy chosen

    Parameters
    ----------
    cands : panda
        The panda data frame with visit information
    rand : integer
        The number of random items to return

    Returns
    -------
    panda
        The panda of length rand
    """

    lines = [[(tour.v_lon[i], tour.v_lat[i]), (tour.v_lon[i+1], tour.v_lat[i+1])]
             for i in range(0, len(tour)-1)]
    lc = mc.LineCollection(lines, linewidths=2)
    fig, ax = pl.subplots(figsize=(10, 5))
    ax.set_aspect('equal')
    ax.add_collection(lc)
    ax.autoscale()
    plt.show()
