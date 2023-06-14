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
    # TODO: response.scrape?
    soup = response.soup()

    next_links = set(
        a.get("href") for a in soup.select("#newslist article > h2 > a[href]")
    )
    title = soup.select_one("title").get_text().strip()

    return title, next_links
