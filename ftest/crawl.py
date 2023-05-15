from minet.crawl import Crawler, Spider, CrawlJob
from minet.crawl.spiders import SpiderResult
from minet.crawl.types import CrawlJob, SuccessfulCrawlResult
from minet.web import Response
from urllib.parse import urljoin
from minet.cli.console import console
from minet.extraction import extract, TrafilaturaResult


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


# class CustomSpider(Spider):
#     START_URL = "https://www.lemonde.fr/"

#     def __call__(self, job, response):
#         # self.write("dump.html", response.body, compress=True)
#         return


# with Crawler(CustomSpider()) as crawler:
#     for result in crawler:
#         console.print(result, highlight=True)


class ExtractionSpider(Spider):
    START_URLS = [
        "https://www.lemonde.fr/international/article/2023/05/15/elections-en-turquie-recep-tayyip-erdogan-et-kemal-kilicdaroglu-se-preparent-a-un-second-tour-presidentiel-inedit_6173380_3210.html",
        "https://www.lefigaro.fr/faits-divers/reforme-des-retraites-dix-mois-de-prison-contre-un-etudiant-en-marge-d-une-manifestation-a-rennes-20230515",
        "https://www.liberation.fr/culture/cinema/festival-de-cannes-jeanne-du-barry-maiwenn-saoule-au-bourbon-20230515_N2HT26WL4BBCVKVQGPYZ4D2CDI/",
    ]

    def __call__(self, job: CrawlJob, response: Response):
        result = self.submit(extract, response.text())

        return result, None


with Crawler[None, TrafilaturaResult](
    ExtractionSpider(), process_pool_workers=2
) as crawler:
    for result in crawler:
        if not isinstance(result, SuccessfulCrawlResult):
            raise result.error

        console.print(result, highlight=True)
        console.print(result.data.content)
        console.print()
