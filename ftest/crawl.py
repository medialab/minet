from minet.crawl import Crawler, CrawlJob
from minet.web import Response
from urllib.parse import urljoin


def scrape(job: CrawlJob, response: Response):
    soup = response.soup()
    articles = response.soup().select("article")

    titles = [a.select_one("h2").get_text().strip() for a in articles]

    if job.depth > 0:
        return titles, None

    next_link = urljoin(job.url, soup.select_one("a.more").get("href"))

    return titles, [next_link]


with Crawler(scrape) as crawler:
    crawler.enqueue("https://www.echojs.com/latest/0")

    for result in crawler:
        print(1, result)

    crawler.enqueue("https://www.echojs.com/latest/5")

    for result in crawler:
        print(2, result)
