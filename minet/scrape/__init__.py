# =============================================================================
# Minet Scrape Module
# =============================================================================
#
# Module exposing utilities related to minet's scraping DSL.
#
from bs4 import BeautifulSoup
from minet.scrape.apply import apply_scraper


def scrape(scraper, html, engine='lxml'):
    soup = html

    if not isinstance(soup, BeautifulSoup):
        soup = BeautifulSoup(html, engine)

    return apply_scraper(scraper, soup)
