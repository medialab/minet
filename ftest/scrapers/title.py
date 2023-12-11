from minet.scrape import WonderfulSoup
from casanova import RowWrapper


def scrape(row: RowWrapper, soup: WonderfulSoup):
    return {"url": row.url, "title": soup.scrape_one("title")}


def titles(row: RowWrapper, soup: WonderfulSoup):
    yield soup.scrape_one("title")
