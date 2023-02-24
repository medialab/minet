from typing import TypeVar, Mapping, Union, Generic, Optional

from ural import get_domain_name

from minet.web import Response

CrawlJobDataType = TypeVar("CrawlJobDataType", bound=Mapping)
CrawlJobOutputDataType = TypeVar("CrawlJobOutputDataType")


class CrawlJob(Generic[CrawlJobDataType]):
    __slots__ = ("url", "level", "spider", "data", "__has_cached_domain", "__domain")

    url: str
    level: int
    spider: Optional[str]
    data: Optional[CrawlJobDataType]

    # TODO: we should add headers, cookies and such here in the future

    __has_cached_domain: bool
    __domain: Optional[str]

    def __init__(
        self,
        url: str,
        level: int = 0,
        spider: Optional[str] = None,
        data: Optional[CrawlJobDataType] = None,
    ):
        self.url = url
        self.level = level
        self.spider = spider
        self.data = data

        self.__has_cached_domain = False
        self.__domain = None

    def __getstate__(self):
        return (self.url, self.level, self.spider, self.data)

    def __setstate__(self, state):
        self.url = state[0]
        self.level = state[1]
        self.spider = state[2]
        self.data = state[3]

    def id(self) -> str:
        return "%x" % id(self)

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

        return ("<%(class_name)s level=%(level)s url=%(url)s spider=%(spider)s>") % {
            "class_name": class_name,
            "url": self.url,
            "level": self.level,
            "spider": self.spider,
        }


UrlOrCrawlJob = Union[str, CrawlJob[CrawlJobDataType]]


class CrawlResult(Generic[CrawlJobDataType, CrawlJobOutputDataType]):
    __slots__ = ("job", "output", "error", "response")

    job: CrawlJob[CrawlJobDataType]
    output: Optional[CrawlJobOutputDataType]
    error: Optional[Exception]
    response: Optional[Response]

    def __init__(self, job: CrawlJob[CrawlJobDataType]):
        self.job = job
        self.output = None
        self.error = None
        self.response = None

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
