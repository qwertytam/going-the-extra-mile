from requests import get
from zipfile import ZipFile
import os, sqlite3

url = 'https://download.geonames.org/export/dump/US.zip'
data_dir = './data/'
usz_fn = 'US.zip'
ust_fn = 'US.txt'
usdb_fn = 'us-counties.db'
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

with ZipFile(fp, 'r') as zip_ref:
    zpath = zip_ref.extract(ust_fn, path = data_dir)
    zip_ref.close()
    print('Extracted {}'.format(zpath))

fp = data_dir + usdb_fn
conn = sqlite3.connect(fp)

# fn = 'workfile.txt'
# with open(fn, 'w+') as f:
#     f.write('Hello there\n')
#     f.write('What have we written?')
#
# with open(fn, 'r') as f:
#     read_data = f.read()
#     print(read_data)
