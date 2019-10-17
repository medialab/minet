from minet.crawl import crawl
from minet.utils import load_definition

spider = load_definition('./ftest/spiders/echojs_scraper.yml')

crawl(spider)
