# =============================================================================
# Minet Scrape Module
# =============================================================================
#
# Module exposing utilities related to minet's scraping DSL.
#
from bs4 import BeautifulSoup
from minet.scrape.apply import apply_scraper


def scrape(scraper, html, engine='lxml', context=None):
    is_already_soup = isinstance(html, BeautifulSoup)

    if not is_already_soup:
        soup = BeautifulSoup(html, engine)
    else:
        soup = html

    return apply_scraper(
        scraper,
        soup,
        root=soup,
        html=str(soup) if is_already_soup else html,
        context=context
    )


def headers_from_definition(scraper):
    fields = scraper.get('fields')

    if fields is None:
        return ['value']

    return list(scraper['fields'].keys())
