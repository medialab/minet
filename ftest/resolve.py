from minet.utils import resolve, create_safe_pool

URLS = [
  'http://bit.ly/2KkpxiW',
  'https://demo.cyotek.com/features/redirectlooptest.php',
  'https://bit.ly/2gnvlgb'
]

http = create_safe_pool()

for url in URLS:
  print()
  error, stack = resolve(http, url)
  print(error)
  for item in stack:
    print(item)
