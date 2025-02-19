# =============================================================================
# Minet Scrape Module
# =============================================================================
#
# Module exposing utilities related to minet's scraping DSL.
#
from minet.scrape.classes.definition import scrape, DefinitionScraper, validate
from minet.scrape.soup import (
    WonderfulSoup,
    MinetTag as Tag,
    SelectionError,
    ExtractionError,
)
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
    "Tag",
    "SelectionError",
    "ExtractionError",
    "extract_encodings_from_xml",
    "extract_canonical_link",
    "extract_javascript_relocation",
    "extract_meta_refresh",
]
