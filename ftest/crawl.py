from minet.crawl import crawl
from minet.utils import load_definition

spider = load_definition('./ftest/spiders/demosphere.yml')

for result in crawl(spider, throttle=2):
    print(result.job)
