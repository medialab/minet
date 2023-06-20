from minet.web import Response
from minet.crawl import CrawlJob, SpiderResult

# -m 1 -s https://echojs.com/latest

# ---
# start_url: https://echojs.com/latest
# next:
#   scraper:
#     iterator: "#newslist article > h2 > a"
#     item:
#       attr: href
# max_depth: 1
# scraper:
#   item:
#     sel: title


def spider(job: CrawlJob, response: Response) -> SpiderResult:
    soup = response.soup()

    next_links = soup.scrape("#newslist article > h2 > a[href]", "href")
    title = soup.select_one("title", strict=True).get_text()

    return title, next_links
