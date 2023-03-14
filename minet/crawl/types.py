from typing import TypeVar, Mapping, Union, Generic, Optional

from ural import get_domain_name, ensure_protocol

from minet.web import Response

CrawlJobDataType = TypeVar("CrawlJobDataType", bound=Mapping)
CrawlResultDataType = TypeVar("CrawlResultDataType")


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
    depth: int
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
        self.depth = depth if depth is not None else 0
        self.spider = spider
        self.data = data
        self.attempts = 0

        self.__has_cached_domain = False
        self.__domain = None

    def __getstate__(self):
        return (self.url, self.depth, self.spider, self.data, self.attempts)

    def __setstate__(self, state):
        self.url = state[0]
        self.depth = state[1]
        self.spider = state[2]
        self.data = state[3]
        self.attempts = state[4]

        self.__has_cached_domain = False
        self.__domain = None

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
            "<{class_name} depth={depth!r} url={url!r} spider={spider!r} attempts={attempts!r}>"
        ).format(
            class_name=class_name,
            url=self.url,
            depth=self.depth,
            spider=self.spider,
            attempts=self.attempts,
        )


UrlOrCrawlJob = Union[str, CrawlJob[CrawlJobDataType]]


class CrawlResult(Generic[CrawlJobDataType, CrawlResultDataType]):
    __slots__ = ("job", "data", "error", "response", "degree")

    job: CrawlJob[CrawlJobDataType]
    data: Optional[CrawlResultDataType]
    error: Optional[Exception]
    response: Optional[Response]
    degree: int

    def __init__(self, job: CrawlJob[CrawlJobDataType]):
        self.job = job
        self.data = None
        self.error = None
        self.response = None
        self.degree = 0


class ErroredCrawlResult(CrawlResult[CrawlJobDataType, None]):
    job: CrawlJob[CrawlJobDataType]
    data: None
    error: Exception
    response: Optional[Response]
    degree: int

    def __init__(
        self,
        job: CrawlJob[CrawlJobDataType],
        error: Exception,
        response: Optional[Response] = None,
    ):
        self.job = job
        self.data = None
        self.error = error
        self.response = response
        self.degree = 0

    def __repr__(self):
        name = self.__class__.__name__

        return "<{name} url={url!r} error={error}>".format(
            name=name, url=self.job.url, error=self.error.__class__.__name__
        )


class SuccessfulCrawlResult(CrawlResult[CrawlJobDataType, CrawlResultDataType]):
    job: CrawlJob[CrawlJobDataType]
    data: CrawlResultDataType
    error: None
    response: Response
    degree: int

    def __init__(
        self,
        job: CrawlJob[CrawlJobDataType],
        response: Response,
        data: CrawlResultDataType,
        degree: int,
    ):
        self.job = job
        self.data = data
        self.error = None
        self.response = response
        self.degree = degree

    def __repr__(self):
        name = self.__class__.__name__

        return "<{name} url={url!r} status={status!r} degree={degree!r}>".format(
            name=name, url=self.job.url, status=self.response.status, degree=self.degree
        )


SomeCrawlResult = Union[
    ErroredCrawlResult[CrawlJobDataType],
    SuccessfulCrawlResult[CrawlJobDataType, CrawlResultDataType],
]
