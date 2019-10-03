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


def headers_from_definition(scraper):
    fields = scraper.get('fields')

    if fields is None:
        return ['value']

    return list(scraper['fields'].keys())
