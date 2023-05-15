from minet.crawl import Crawler, Spider, CrawlJob
from minet.web import Response
from urllib.parse import urljoin
from minet.cli.console import console


# def scrape(job: CrawlJob, response: Response):
#     soup = response.soup()
#     articles = response.soup().select("article")

#     titles = [a.select_one("h2").get_text().strip() for a in articles]

#     if job.depth > 0:
#         return titles, None

#     next_link = urljoin(job.url, soup.select_one("a.more").get("href"))

#     return titles, [next_link]


# with Crawler.from_definition("./ftest/crawlers/echojs_crawl.yml") as crawler:
#     for result in crawler:
#         console.print(result.job, highlight=True)
#         console.print(result, highlight=True)


class CustomSpider(Spider):
    START_URL = "https://www.lemonde.fr/"

    def __call__(self, job, response):
        # self.write("dump.html", response.body, compress=True)
        return


with Crawler(CustomSpider()) as crawler:
    for result in crawler:
        console.print(result, highlight=True)
