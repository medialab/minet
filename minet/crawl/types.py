from typing import TypeVar, Mapping, Union, Generic, Optional

from ural import get_domain_name, ensure_protocol

from minet.web import Response

CrawlJobDataType = TypeVar("CrawlJobDataType", bound=Mapping)
CrawlJobOutputDataType = TypeVar("CrawlJobOutputDataType")


class CrawlJob(Generic[CrawlJobDataType]):
    __slots__ = (
        "url",
        "depth",
        "spider",
        "data",
        "attempts",
        "__has_cached_domain",
        "__domain",
    )

    url: str
    depth: Optional[int]
    spider: Optional[str]
    data: Optional[CrawlJobDataType]
    attempts: int

    # TODO: we should add headers, cookies and such here in the future

    __has_cached_domain: bool
    __domain: Optional[str]

    def __init__(
        self,
        url: str,
        depth: Optional[int] = None,
        spider: Optional[str] = None,
        data: Optional[CrawlJobDataType] = None,
    ):
        self.url = ensure_protocol(url).strip()
        self.depth = depth
        self.spider = spider
        self.data = data
        self.attempts = 0

        self.__has_cached_domain = False
        self.__domain = None

    def __getstate__(self):
        return (self.url, self.depth, self.spider, self.data)

    def __setstate__(self, state):
        self.url = state[0]
        self.depth = state[1]
        self.spider = state[2]
        self.data = state[3]

    @property
    def domain(self) -> Optional[str]:
        if self.__has_cached_domain:
            return self.__domain

        if self.url is not None:
            self.__domain = get_domain_name(self.url)

        self.__has_cached_domain = True

        return self.__domain

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            "<{class_name} depth={depth!r}url={url!r} spider={spider!r} attempts={attempts!r}>"
        ).format(
            class_name=class_name,
            url=self.url,
            depth=self.depth,
            spider=self.spider,
            attempts=self.attempts,
        )


UrlOrCrawlJob = Union[str, CrawlJob[CrawlJobDataType]]


class CrawlResult(Generic[CrawlJobDataType, CrawlJobOutputDataType]):
    __slots__ = ("job", "output", "error", "response", "degree")

    job: CrawlJob[CrawlJobDataType]
    output: Optional[CrawlJobOutputDataType]
    error: Optional[Exception]
    response: Optional[Response]
    degree: int

    def __init__(self, job: CrawlJob[CrawlJobDataType]):
        self.job = job
        self.output = None
        self.error = None
        self.response = None
        self.degree = 0

    def __repr__(self):
        name = self.__class__.__name__

        if not self.response:
            return "<{name} url={url!r} pending!>".format(name=name, url=self.job.url)

        if self.error:
            return "<{name} url={url!r} error={error}>".format(
                name=name, url=self.job.url, error=self.error.__class__.__name__
            )

        assert self.response is not None

        return "<{name} url={url!r} status={status!r}>".format(
            name=name, url=self.job.url, status=self.response.status
        )
