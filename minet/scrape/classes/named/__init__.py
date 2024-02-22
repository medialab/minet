from typing import Dict, Type
from .types import NamedScraper

from .canonical import CanonicalScraper
from .europresse import EuropresseScraper
from .images import ImagesScraper
from .metas import MetasScraper
from .rss import RssScraper
from .title import TitleScraper
from .urls import UrlsScraper

NAMED_SCRAPERS: Dict[str, Type[NamedScraper]] = {
    s.name: s
    for s in [
        TitleScraper,
        CanonicalScraper,
        UrlsScraper,
        ImagesScraper,
        MetasScraper,
        RssScraper,
        EuropresseScraper,
    ]
}
