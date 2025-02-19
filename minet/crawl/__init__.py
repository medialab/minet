from minet.crawl.types import (
    CrawlResult,
    AnyCrawlResult,
    SuccessfulCrawlResult,
    ErroredCrawlResult,
    CrawlJob,
    CrawlTarget,
    UrlOrCrawlTarget,
)
from minet.crawl.state import CrawlerState
from minet.crawl.spiders import (
    Spider,
    SpiderResult,
    SpiderNextTargets,
    FunctionSpider,
    BasicSpider,
)
from minet.crawl.crawler import Crawler, AnySpider, SpiderDeclaration

__all__ = [
    "CrawlResult",
    "AnyCrawlResult",
    "SuccessfulCrawlResult",
    "ErroredCrawlResult",
    "CrawlJob",
    "CrawlTarget",
    "UrlOrCrawlTarget",
    "CrawlerState",
    "Spider",
    "SpiderResult",
    "SpiderNextTargets",
    "FunctionSpider",
    "BasicSpider",
    "Crawler",
    "AnySpider",
    "SpiderDeclaration",
]
