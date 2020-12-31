import getopt
import sys
import tourroute


def main(argv):
    help_str = 'tr_exec.py -api <apikey>'
    try:
        opts, args = getopt.getopt(argv, 'api:', 'apikey=')
    except getopt.GetoptError:
        print(help_str)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help_str)
            sys.exit()
        elif opt in ('-api', '--apikey'):
            return arg
        else:
            print('Unrecognised command line argument(s)')
            print(help_str)


if __name__ == '__main__':

    apikey = main(sys.argv[1:])
    print(apikey)

    tr = tourroute.TourRoute('../out/tour.csv')
    tr_slices = tr.slices()
    dist, dur = tourroute.get_tour_distdur(apikey, tr_slices)
    print(f'Total duration is {dur:,} seconds and distance is {dist:,} metres')
