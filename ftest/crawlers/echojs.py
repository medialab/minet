from minet.web import Response
from minet.crawl import CrawlJob, SpiderResult, Spider, CrawlTarget, Crawler
from minet.scrape import WonderfulSoup

START_URL = "https://echojs.com/latest"


def scrape(soup: WonderfulSoup) -> SpiderResult:
    next_links = soup.scrape("#newslist article > h2 > a[href]", "href")
    title = soup.select_one("title")

    return title.get_text() if title is not None else None, next_links


def spider(job: CrawlJob, response: Response) -> SpiderResult:
    return scrape(response.soup())


class EchoJSSpider(Spider):
    START_URL = "https://echojs.com/latest"

    def process(self, job: CrawlJob, response: Response) -> SpiderResult:
        return scrape(response.soup())


spider_instance = EchoJSSpider()


class DummyEchoJSSpider(Spider):
    START_URL = "https://echojs.com/latest"

    def process(self, job, response):
        return


class EchoJSStartSpider(Spider):
    START_URL = "https://echojs.com/latest"

    def process(self, job: CrawlJob, response: Response) -> SpiderResult:
        next_links = response.soup().scrape("#newslist article > h2 > a[href]", "href")
        next_targets = [CrawlTarget(url=link, spider="article") for link in next_links]

        return job.group, next_targets


class ArticleSpider(Spider):
    def process(self, job: CrawlJob, response: Response) -> SpiderResult:
        title = response.soup().scrape_one("title")

        return title, None


spiders = {"start": EchoJSStartSpider(), "article": ArticleSpider()}


class EchoJSCrawler(Crawler):
    def __init__(self, **kwargs):
        super().__init__(EchoJSSpider(), **kwargs)


def factory(**crawler_kwargs):
    return EchoJSCrawler(**crawler_kwargs)


def emulation_factory(**crawler_kwargs):
    async def init(context):
        print(context)

    return Crawler(
        EchoJSSpider(),
        browser_emulation=True,
        browser_kwargs={"adblock": True},
        browser_context_init=init,
        **crawler_kwargs,
    )
