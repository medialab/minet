# =============================================================================
# Minet Scrape Module
# =============================================================================
#
# Module exposing utilities related to minet's scraping DSL.
#
from minet.scrape.scraper import scrape, Scraper, validate
from minet.scrape.soup import WonderfulSoup
from minet.scrape.regex import (
    extract_encodings_from_xml,
    extract_canonical_link,
    extract_javascript_relocation,
    extract_meta_refresh,
)

__all__ = [
    "scrape",
    "Scraper",
    "validate",
    "WonderfulSoup",
    "extract_encodings_from_xml",
    "extract_canonical_link",
    "extract_javascript_relocation",
    "extract_meta_refresh",
]
