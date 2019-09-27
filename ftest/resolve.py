# from minet.utils import resolve, create_safe_pool

# URLS = [
#   'http://bit.ly/2KkpxiW',
#   'https://demo.cyotek.com/features/redirectlooptest.php',
#   'https://bit.ly/2gnvlgb'
# ]

# http = create_safe_pool()

# for url in URLS:
#   print()
#   error, stack = resolve(http, url)
#   print(error)
#   for item in stack:
#     print(item)

import csv
from minet import multithreaded_resolve
from tqdm import tqdm

with open('./ftest/resources/resolutions.csv') as f:
    reader = csv.DictReader(f)

    for result in tqdm(multithreaded_resolve(reader, key=lambda x: x['url'], threads=100), total=10000):
        pass
