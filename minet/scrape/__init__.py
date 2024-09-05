# =============================================================================
# Minet Scrape Module
# =============================================================================
#
# Module exposing utilities related to minet's scraping DSL.
#
from minet.scrape.classes.definition import scrape, DefinitionScraper, validate
from minet.scrape.soup import WonderfulSoup, SelectionError
from minet.scrape.regex import (
    extract_encodings_from_xml,
    extract_canonical_link,
    extract_javascript_relocation,
    extract_meta_refresh,
)

__all__ = [
    "scrape",
    "DefinitionScraper",
    "validate",
    "WonderfulSoup",
    "SelectionError",
    "extract_encodings_from_xml",
    "extract_canonical_link",
    "extract_javascript_relocation",
    "extract_meta_refresh",
]
