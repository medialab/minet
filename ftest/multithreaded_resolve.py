# import csv
# from minet import multithreaded_resolve
# from tqdm import tqdm

# with open('./ftest/resources/resolutions.csv') as f, \
#      open('./ftest/resolved.csv', 'w') as of:
#     reader = csv.DictReader(f)
#     writer = csv.writer(of)
#     writer.writerow(['original', 'current', 'error', 'type'])

#     for result in tqdm(multithreaded_resolve(reader, key=lambda x: x['url'], threads=100, follow_js_relocation=True), total=10000):
#         stack = result.stack
#         error = result.error

#         for redirection in stack:
#             writer.writerow([
#                 result.item['url'],
#                 redirection.url,
#                 str(error) if error else '',
#                 redirection.type
#             ])

from minet import multithreaded_resolve
from log import URLS

for result in multithreaded_resolve(URLS[:600], threads=100):
    print(result.error, result.url)
