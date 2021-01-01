

class _TourRoute(object):
    def __init__(self, lats, lngs, names, states, seats):
        '''
        Args:
            lats ([float]): Latitudes for tour stop points
            lngs ([float]): Longitudes for tour stop points
            names ([strings]): County names for each tour stop point
            states ([strings]): County states for each tour stop point
            seats ([strings]): County seat names for each tour stop point
        '''
        self._points = [_format_tour_points(lat, lng, name, state, seat) for lat, lng, name, state, seat in zip(lats, lngs, names, states, seats)]

    def write_to_js(self, w, tour_name=optRoute):
        '''
        Write the TourRoute to a javascript file
        Args:
            w (_Writer): Writer used to write the TourRoute

        Optional:
            tour_name (string): Variable name to be used in the output file.
                Defaults to `optRoute`.
        '''
        w.write(f'var {tour_name} = [')
        w.indent()
        [w.write(f'{point}') for point in self._points]
        w.dedent()
        w.write('];')
        w.write()
