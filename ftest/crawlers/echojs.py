from minet.web import Response
from minet.crawl import CrawlJob, SpiderResult, Spider
from minet.scrape import WonderfulSoup

# https://echojs.com/latest


def scrape(soup: WonderfulSoup) -> SpiderResult:
    next_links = soup.scrape("#newslist article > h2 > a[href]", "href")
    title = soup.select_one("title", strict=True).get_text()

    return title, next_links


def spider(job: CrawlJob, response: Response) -> SpiderResult:
    return scrape(response.soup())


class EchoJSSpider(Spider):
    def process(self, job: CrawlJob, response: Response) -> SpiderResult:
        return scrape(response.soup())
