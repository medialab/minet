# =============================================================================
# Minet Scrape Module
# =============================================================================
#
# Module exposing utilities related to minet's scraping DSL.
#
from minet.scrape.scraper import scrape, Scraper, validate
from minet.scrape.soup import WonderfulSoup

__all__ = ["scrape", "Scraper", "validate", "WonderfulSoup"]
