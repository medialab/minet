from minet.utils import resolve, create_safe_pool

URLS = [
  'http://bit.ly/2KkpxiW',
  'https://demo.cyotek.com/features/redirectlooptest.php',
  'https://bit.ly/2gnvlgb',
  'http://bit.ly/2YupNmj',
  # 'http://www.outremersbeyou.com/talent-de-la-semaine-la-designer-comorienne-aisha-wadaane-je-suis-fiere-de-mes-origines/'
]

http = create_safe_pool()

for url in URLS:
  print()
  error, stack = resolve(http, url)
  print(error)
  for item in stack:
    print(item)

# import csv
# from minet import multithreaded_resolve
# from tqdm import tqdm

# with open('./ftest/resources/resolutions.csv') as f, \
#      open('./ftest/resolved.csv', 'w') as of:
#     reader = csv.DictReader(f)
#     writer = csv.writer(of)
#     writer.writerow(['original', 'resolved', 'error'])

#     for result in tqdm(multithreaded_resolve(reader, key=lambda x: x['url'], threads=100), total=10000):
#         stack = result.stack
#         error = result.error

#         original = stack[0][1] if stack else ''
#         last = stack[-1][1] if stack else ''

#         writer.writerow([
#             original,
#             last if last != original else '',
#             str(error) if error else ''
#         ])
