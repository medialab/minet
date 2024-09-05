from typing import TYPE_CHECKING

from minet.exceptions import MinetError

if TYPE_CHECKING:
    from minet.crawl.types import CrawlJob
    from minet.web import Response


class CrawlerError(MinetError):
    pass


class CrawlerAlreadyFinishedError(CrawlerError):
    pass


class CrawlerSpiderProcessError(CrawlerError):
    def __init__(self, reason: Exception, job: "CrawlJob", response: "Response"):
        self.reason = reason
        self.job = job
        self.response = response
        super().__init__(str(reason))
