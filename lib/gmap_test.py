import googlemaps
import numpy as np
import pandas as pd

gmaps = googlemaps.Client(key='api_key')

dir_result = gmaps.directions(origin="Sydney Town Hall",
                                     destination="Parramatta, NSW",
                                     waypoints=["Newcastle, NSW",
                                                "Canberra, ACT"],
                                     mode="driving",
                                     units="metric")

result_plines = []
result_coords = []

for leg in dir_result[0]['legs']:
    start_addr = leg['start_address']
    end_addr = leg['end_address']
    ldist = leg['distance']['value']
    ldur = leg['duration']['value']

    print(f'\nStarting from:{start_addr}')
    print(f'and ending at:{end_addr}')
    print(f'the leg has a distance of {ldist:,} m and takes {ldur:,} seconds')

    sdist = 0

    for step in leg['steps']:
        pline_pts = step['polyline']['points']
        dist = step['distance']['value']
        result_plines = np.append(result_plines, pline_pts)

        sdist = sdist + dist
        if 'steps' in step:
            for stepp in step['steps']:
                pline_pts = step['polyline']['points']
                print('Hello!!')

    print(f'sdist is {sdist:,} m which is {sdist - ldist:,} longer than ldist')

result_plines = pd.DataFrame(result_plines)
result_plines.to_csv('plines.csv', index=False, header=False)
