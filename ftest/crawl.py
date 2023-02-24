from minet.crawl import Crawler, Spider, FunctionSpider, CrawlJob
from minet.web import Response


def scrape_articles(job: CrawlJob, response: Response):
    articles = response.soup().select("article")

    titles = [a.select_one("h2").get_text().strip() for a in articles]

    return titles, None


spider = FunctionSpider(scrape_articles, start_jobs=["https://www.echojs.com/"])


with Crawler(spider) as crawler:
    for result in crawler:
        print(result)

        if result.error:
            print(result.error)
        elif result.output:
            print(result.output)
