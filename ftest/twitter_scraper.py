import json
from minet.twitter.api_scraper import TwitterAPIScraper

scraper = TwitterAPIScraper()

QUERIES = [
  'covid #5gcovid #microchipping #vaccine #5g',
  'My "It\'s official government policy that we don\'t engage in regime change" T-shirt has people asking a lot of questions already answered by my shirt.',
  'from:EmmanuelMacron'
]

data = scraper.request_search(QUERIES[-1], dump=True)

with open('./dump.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
