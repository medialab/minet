from minet.crawl import Crawler, Spider, CrawlJob
from minet.web import Response


class EchoJSSpider(Spider):
    def start_jobs(self):
        yield "https://www.echojs.com/"

    def __call__(self, job: CrawlJob, response: Response):
        articles = response.soup().select("article")

        titles = [a.select_one("h2").get_text().strip() for a in articles]

        return titles, None


with Crawler(EchoJSSpider()) as crawler:
    for result in crawler:
        print(result)

        if result.error:
            print(result.error.reason)
        elif result.scraped:
            print(result.scraped)
