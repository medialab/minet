from minet.web import Response
from minet.crawl import CrawlJob, SpiderResult, Spider, CrawlTarget, Crawler
from minet.scrape import WonderfulSoup

START_URL = "https://echojs.com/latest"


def scrape(soup: WonderfulSoup) -> SpiderResult:
    next_links = soup.scrape("#newslist article > h2 > a[href]", "href")
    title = soup.select_one("title", strict=True).get_text()

    return title, next_links


def spider(job: CrawlJob, response: Response) -> SpiderResult:
    return scrape(response.soup())


class EchoJSSpider(Spider):
    START_URL = "https://echojs.com/latest"

    def process(self, job: CrawlJob, response: Response) -> SpiderResult:
        return scrape(response.soup())


spider_instance = EchoJSSpider()


class EchoJSStartSpider(Spider):
    START_URL = "https://echojs.com/latest"

    def process(self, job: CrawlJob, response: Response) -> SpiderResult:
        next_links = response.soup().scrape("#newslist article > h2 > a[href]", "href")
        next_targets = [CrawlTarget(url=link, spider="article") for link in next_links]

        return job.domain, next_targets


class ArticleSpider(Spider):
    def process(self, job: CrawlJob, response: Response) -> SpiderResult:
        title = response.soup().scrape_one("title")

        return title, None


spiders = {"start": EchoJSStartSpider(), "article": ArticleSpider()}


class EchoJSCrawler(Crawler):
    def __init__(self):
        super().__init__(EchoJSSpider())
