import csv, os, sqlite3

from requests import get
from zipfile import ZipFile
from os import mkdir
from os.path import exists, join

url = 'https://download.geonames.org/export/dump/US.zip'
data_dir = join('..', 'data')
zip_fnm = 'US.zip'
txt_fnm = 'US.txt'
db_fnm = 'counties.sqlite'
counties_csv_fnm = 'counties.csv'
county_seat_csv_fnm = 'county-seats.csv'

if not exists(data_dir):
    mkdir(data_dir)
    print('Created dir {}'.format(data_dir))

fp = join(data_dir, zip_fnm)

with open(fp, 'wb') as f:
    print('Downloading {}'.format(fp))
    response = get(url, stream=True)
    total_length = response.headers.get('content-length')

    if total_length is None: # no content length header
        f.write(response.content)
    else:
        dl = 0
        total_length = int(total_length)
        for data in response.iter_content(chunk_size=4096):
            dl += len(data)
            f.write(data)
            done = int(50 * dl / total_length)
            print("\r[{}{}] {}%".format('=' * done, ' ' * (50-done), done * 2), end = '\r')

# Retrieve HTTP meta-data
print('\nHTTP status {}'.format(response.status_code))
print('Content type {}'.format(response.headers['content-type']))
print('Enconding {}\n'.format(response.encoding))

with ZipFile(fp, 'r') as zip_ref:
    print('Unzipping {}'.format(fp))
    zpath = zip_ref.extract(txt_fnm, path = data_dir)
    zip_ref.close()
    print('Extracted {}'.format(zpath))
os.remove(fp)
print('Deleted {}\n'.format(fp))

infile_fp = join(data_dir, txt_fnm)
dbfile_fp = join(data_dir, db_fnm)

# Create table and read data for each county
with open(infile_fp) as incsv:
    print('Reading {} into county SQL table'.format(infile_fp))
    reader = csv.reader(incsv, delimiter="\t")
    conn = sqlite3.connect(dbfile_fp)
    c = conn.cursor()
    c.execute('''CREATE TABLE county
             (name, latitude, longitude, feature_code, subcountry_code, admin2_code, geonameid)''')
    for geonameid, name, asciiname, alternatenames, latitude, longitude, \
      featureclass, featurecode, countrycode, cc2, admin1code, admin2code, \
      admin3code, admin4code, population, elevation, dem, timezone, \
      modificationdate in reader:
        feature_class = featureclass
        feature_code = featurecode
        country_code = countrycode
        subcountry_code = admin1code
        admin2_code = admin2code
        c.execute("INSERT INTO county VALUES (?, ?, ?, ?, ?, ?, ?)", (name, latitude, longitude, feature_code, subcountry_code, admin2_code, geonameid))

    c.execute("DELETE FROM county WHERE feature_code <> 'ADM2'")
    conn.commit()
    conn.close()
print('Created and added data to county SQL table\n')

# Create table and read data for each county seat
with open(infile_fp) as incsv:
    print('Reading {} into county_seat SQL table'.format(infile_fp))
    reader = csv.reader(incsv, delimiter="\t")
    conn = sqlite3.connect(dbfile_fp)
    c = conn.cursor()
    c.execute('''CREATE TABLE county_seat
             (name, latitude, longitude, feature_code, subcountry_code, admin2_code, geonameid)''')
    for geonameid, name, asciiname, alternatenames, latitude, longitude, \
      featureclass, featurecode, countrycode, cc2, admin1code, admin2code, \
      admin3code, admin4code, population, elevation, dem, timezone, \
      modificationdate in reader:
        feature_class = featureclass
        feature_code = featurecode
        country_code = countrycode
        subcountry_code = admin1code
        admin2_code = admin2code
        c.execute("INSERT INTO county_seat VALUES (?, ?, ?, ?, ?, ?, ?)", (name, latitude, longitude, feature_code, subcountry_code, admin2_code, geonameid))

    c.execute("DELETE FROM county_seat WHERE feature_code <> 'PPLA2'")
    conn.commit()
    conn.close()
print('Created and added data to county_seat SQL table\n')

# Delete the text file
os.remove(infile_fp)
print('Deleted {}\n'.format(infile_fp))

# Write the county data to csv file
outfile_fp = join(data_dir, counties_csv_fnm)
COUNTY_HEADERS = ['name', 'latitude', 'longitude', 'state',
'admin2_code', 'geonameid']
with open(outfile_fp, 'w') as outcsv:
    print('Writing county SQL table to {}'.format(outfile_fp))
    writer = csv.writer(outcsv, lineterminator="\n")
    writer.writerow(COUNTY_HEADERS)
    conn = sqlite3.connect(dbfile_fp)
    c = conn.cursor()
    sql = '''SELECT
                name,
                latitude,
                longitude,
                subcountry_code,
                admin2_code,
                geonameid
             FROM county
             '''
    for name, latitude, longitude, subcountry_code, admin2_code, geonameid in c.execute(sql):
        row = (name, latitude, longitude, subcountry_code, admin2_code, geonameid)
        writer.writerow(row)
    conn.close()
print('Created and added data to {}'.format(outfile_fp))

# Write the county seat data to csv file
outfile_fp = join(data_dir, county_seat_csv_fnm)
COUNTYSEAT_HEADERS = ['name', 'latitude', 'longitude', 'state',
'admin2_code', 'geonameid']
with open(outfile_fp, 'w') as outcsv:
    print('Writing county_seat SQL table to {}'.format(outfile_fp))
    writer = csv.writer(outcsv, lineterminator="\n")
    writer.writerow(COUNTYSEAT_HEADERS)
    conn = sqlite3.connect(dbfile_fp)
    c = conn.cursor()
    sql = '''SELECT
                name,
                latitude,
                longitude,
                subcountry_code,
                admin2_code,
                geonameid
             FROM county_seat
             '''
    for name, latitude, longitude, subcountry_code, admin2_code, geonameid in c.execute(sql):
        row = (name, latitude, longitude, subcountry_code, admin2_code, geonameid)
        writer.writerow(row)
    conn.close()
print('Created and added data to {}'.format(outfile_fp))

# Remove the database file
os.remove(dbfile_fp)
print('Deleted {}\n'.format(dbfile_fp))

print('#<<<<   Script completed   >>>>#')
