import json
from minet.twitter.api_scraper import TwitterAPIScraper
import csv
import sys

scraper = TwitterAPIScraper()

QUERIES = [
  'covid #5gcovid #microchipping #vaccine #5g',
  'My "It\'s official government policy that we don\'t engage in regime change" T-shirt has people asking a lot of questions already answered by my shirt.',
  'from:EmmanuelMacron'
]

#data = scraper.request_search(QUERIES[0], dump=False)
#print(data)

#for tweet, meta in scraper.request_search('cancer'):
#  print(meta)

# for data in scraper.request_search_user('cancer')
#   with open('./dump.json', 'w') as f:
#     json.dump(data, f, ensure_ascii=False, indent=2)

writer = csv.writer(sys.stdout)
writer.writerow(['screen_name'])
for user in scraper.search_user('my'):
  writer.writerow([user['screen_name']])