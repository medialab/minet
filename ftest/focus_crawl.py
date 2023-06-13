from minet.crawl.focus import FocusSpider
from minet.crawl import Crawler
import warnings


def test1():

    warnings.filterwarnings("ignore", module="bs4")

    url = ""
    pattern = r"\\n"
    # print(pattern)

    spider = FocusSpider([url], 1, pattern, irrelevant_continue=True)

    crawler = Crawler(spider)

    with crawler:
        for result in crawler:
            if not result.error:
                print(result.as_csv_row() + [result.data.relevant])


test1()
