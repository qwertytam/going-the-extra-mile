import requests, os, sys
import zipfile

url = 'https://download.geonames.org/export/dump/US.zip'
fn = 'US.zip'
# with open(fn, 'wb') as f:
#     print('Downloading {}'.format(fn))
#     response = requests.get(url, stream=True)
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

with zipfile.ZipFile(fn, 'r') as zip_ref:
    zip_ref.extractall()

# fn = 'workfile.txt'
# with open(fn, 'w+') as f:
#     f.write('Hello there\n')
#     f.write('What have we written?')
#
# with open(fn, 'r') as f:
#     read_data = f.read()
#     print(read_data)
