# =============================================================================
# Minet Spiders
# =============================================================================
#
#
from typing import (
    TYPE_CHECKING,
    Optional,
    Tuple,
    Union,
    Callable,
    Iterable,
    Generic,
)

if TYPE_CHECKING:
    from minet.crawl.crawler import Crawler

from minet.crawl.types import (
    UrlOrCrawlTarget,
    CrawlTarget,
    CrawlJob,
    CrawlJobDataType,
    CrawlResultDataType,
)
from minet.web import Response
from minet.utils import PseudoFStringFormatter

FORMATTER = PseudoFStringFormatter()

SpiderNextTargets = Optional[Iterable[UrlOrCrawlTarget[CrawlJobDataType]]]
SpiderResult = Optional[Tuple[CrawlResultDataType, SpiderNextTargets[CrawlJobDataType]]]


class Spider(Generic[CrawlJobDataType, CrawlResultDataType]):
    START_URL: Optional[str] = None
    START_URLS: Optional[Iterable[str]] = None
    START_TARGET: Optional[CrawlTarget[CrawlJobDataType]] = None
    START_TARGETS: Optional[Iterable[CrawlTarget[CrawlJobDataType]]] = None

    @property
    def crawler(self) -> "Crawler":
        c = getattr(self, "_crawler", None)

        if c is None:
            raise RuntimeError("spider has no attached crawler")

        return c

    def attach(self, crawler: "Crawler"):
        if getattr(self, "_crawler", None) is not None:
            raise TypeError("spider is already attached to a crawler")

        self._crawler = crawler

    def detach(self):
        if getattr(self, "_crawler", None) is None:
            raise TypeError("spider is not attached to a crawler")

    def start(self) -> Optional[Iterable[UrlOrCrawlTarget[CrawlJobDataType]]]:
        return None

    def process(
        self, job: CrawlJob[CrawlJobDataType], response: Response
    ) -> SpiderResult[CrawlResultDataType, CrawlJobDataType]:
        raise NotImplementedError

    def __repr__(self):
        class_name = self.__class__.__name__

        return "<%(class_name)s>" % {"class_name": class_name}

    def write(
        self,
        filename: str,
        contents: Union[str, bytes],
        compress: bool = False,
        relative: bool = False,
    ) -> str:
        return self.crawler.write(
            filename, contents, compress=compress, relative=relative
        )

    def submit(self, fn, *args, **kwargs):
        return self.crawler.submit(fn, *args, **kwargs)


FunctionSpiderCallable = Callable[
    [CrawlJob[CrawlJobDataType], Response],
    SpiderResult[CrawlResultDataType, CrawlJobDataType],
]


class FunctionSpider(Spider[CrawlJobDataType, CrawlResultDataType]):
    fn: FunctionSpiderCallable[CrawlJobDataType, CrawlResultDataType]

    def __init__(
        self,
        fn: FunctionSpiderCallable[CrawlJobDataType, CrawlResultDataType],
        start: Optional[Iterable[UrlOrCrawlTarget[CrawlJobDataType]]] = None,
    ):
        self.fn = fn
        self.__start_targets = start

    def start(self) -> Optional[Iterable[UrlOrCrawlTarget[CrawlJobDataType]]]:
        return self.__start_targets

    def process(
        self, job: CrawlJob[CrawlJobDataType], response: Response
    ) -> SpiderResult[CrawlResultDataType, CrawlJobDataType]:
        return self.fn(job, response)
