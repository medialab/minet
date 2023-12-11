from typing import Union

from bs4 import BeautifulSoup

from minet.scrape.soup import WonderfulSoup

AnyScrapableTarget = Union[str, WonderfulSoup, BeautifulSoup]
