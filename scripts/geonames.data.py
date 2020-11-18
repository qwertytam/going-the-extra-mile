from requests import get
from zipfile import ZipFile
import csv, os, sqlite3

url = 'https://download.geonames.org/export/dump/US.zip'
data_dir = './data/'
usz_fn = 'US.zip'
ust_fn = 'US.txt'
usdb_fn = 'us-counties.sqlite'
fp = data_dir + usz_fn

# with open(fp, 'wb') as f:
#     print('Downloading {}'.format(fp))
#     response = get(url, stream=True)
#     total_length = response.headers.get('content-length')
#
#     if total_length is None: # no content length header
#         f.write(response.content)
#     else:
#         dl = 0
#         total_length = int(total_length)
#         for data in response.iter_content(chunk_size=4096):
#             dl += len(data)
#             f.write(data)
#             done = int(50 * dl / total_length)
#             print("\r[{}{}] {}%".format('=' * done, ' ' * (50-done), done * 2), end = '\r')
#
# # Retrieve HTTP meta-data
# print('\nHTTP status {}'.format(response.status_code))
# print('Content type {}'.format(response.headers['content-type']))
# print('Enconding {}'.format(response.encoding))
#
# with ZipFile(fp, 'r') as zip_ref:
#     zpath = zip_ref.extract(ust_fn, path = data_dir)
#     zip_ref.close()
#     print('Extracted {}'.format(zpath))

INFILE = data_dir + ust_fn
DBFILE = data_dir + usdb_fn

with open(INFILE) as incsv:
    reader = csv.reader(incsv, delimiter="\t")
    conn = sqlite3.connect(DBFILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE county
             (name, latitude, longitude, feature_class, feature_code, country_code, subcountry_code, admin1_code, admin2_code, admin3_code, admin4_code, geonameid)''')
    for geonameid, name, asciiname, alternatenames, latitude, longitude, \
      featureclass, featurecode, countrycode, cc2, admin1code, admin2code, \
      admin3code, admin4code, population, elevation, dem, timezone, \
      modificationdate in reader:
        # name = name.decode('utf8')
        feature_class = featureclass
        feature_code = featurecode
        country_code = countrycode
        subcountry_code = admin1code
        admin1_code = admin1code
        admin2_code = admin2code
        admin3_code = admin3code
        admin4_code = admin4code
        # geonameid = geonameid.decode('utf8')
        c.execute("INSERT INTO county VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, latitude, longitude, feature_class, feature_code, country_code, subcountry_code, admin1_code, admin2_code, admin3_code, admin4_code, geonameid))

    c.execute("DELETE FROM county WHERE feature_code <> 'ADM2'")
    conn.commit()
    conn.close()

# os.remove(DBFILE)

# fn = 'workfile.txt'
# with open(fn, 'w+') as f:
#     f.write('Hello there\n')
#     f.write('What have we written?')
#
# with open(fn, 'r') as f:
#     read_data = f.read()
#     print(read_data)
