from minet.scrape import WonderfulSoup
from casanova import RowWrapper


def scrape(row: RowWrapper, soup: WonderfulSoup):
    return soup.scrape_one("title")
