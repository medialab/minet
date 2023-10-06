from typing import TypeVar, Union, Generic, Optional, List

import json
from nanoid import generate
from ebbe import format_repr
from functools import partial

from minet.web import Response
from minet.encodings import normalize_encoding
from minet.serialization import serialize_error_as_slug

CrawlJobDataType = TypeVar("CrawlJobDataType")
CrawlResultDataType = TypeVar("CrawlResultDataType")


class CrawlTarget(Generic[CrawlJobDataType]):
    """
    This class represent a crawl target, i.e. at least a URL, and should be
    used by end-users when they need to specify what they want to crawl more
    precisely (i.e. if they need to switch spiders, have a custom depth or
    rely on some necessary data that will be passed along).
    """

    __slots__ = ("url", "depth", "spider", "priority", "data")

    url: str
    depth: Optional[int]
    spider: Optional[str]
    priority: int
    data: Optional[CrawlJobDataType]

    def __init__(
        self,
        url: str,
        depth: Optional[int] = None,
        spider: Optional[str] = None,
        priority: int = 0,
        data: Optional[CrawlJobDataType] = None,
    ) -> None:
        if not isinstance(url, str):
            raise TypeError("url should be a string")

        self.url = url

        if depth is not None and not isinstance(depth, int):
            raise TypeError("depth should be an int")

        self.depth = depth

        if spider is not None and not isinstance(spider, str):
            raise TypeError("spider should be a string")

        if not isinstance(priority, int):
            raise TypeError("depth should be an int")

        self.spider = spider
        self.priority = priority
        self.data = data

    def __eq__(self, other):
        if not isinstance(other, CrawlTarget):
            return False

        for k in self.__slots__:
            if getattr(self, k) != getattr(other, k):
                return False

        return True

    def __repr__(self):
        return format_repr(
            self,
            ("url", "spider", "depth", ("priority", self.priority or None), "data"),
            conditionals=("spider", "data", "depth", "priority"),
        )


UrlOrCrawlTarget = Union[str, CrawlTarget[CrawlJobDataType]]


generate_crawl_job_id = partial(
    generate,
    alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    size=12,
)


class CrawlJob(Generic[CrawlJobDataType]):
    """
    This class represents an actual job that will be queued by the crawler. It
    should not be created by users themselves as they are inferred from
    a CrawlTarget instead.

    This class should be pickle-safe as it will be serialized by persistent
    queues.
    """

    __slots__ = ("id", "url", "group", "depth", "spider", "priority", "data", "parent")

    id: str
    url: str
    group: Optional[str]
    depth: int
    spider: Optional[str]
    priority: int
    data: Optional[CrawlJobDataType]
    parent: Optional[str]

    # TODO: we should add headers, method, cookies and such here in the future,
    # but for now, a request_args override can do the trick based on job data

    @classmethod
    def fieldnames(cls):
        return [slot for slot in cls.__slots__ if not slot.startswith("_")]

    def __init__(
        self,
        url: str,
        id: Optional[str] = None,
        group: Optional[str] = None,
        depth: Optional[int] = None,
        spider: Optional[str] = None,
        priority: int = 0,
        data: Optional[CrawlJobDataType] = None,
        parent: Optional[str] = None,
    ):
        self.id = id if id is not None else generate_crawl_job_id()
        self.url = url
        self.group = group
        self.depth = depth if depth is not None else 0
        self.spider = spider
        self.priority = priority
        self.data = data
        self.parent = parent

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, CrawlJob):
            return False

        for k in self.__slots__:
            if getattr(self, k) != getattr(other, k):
                return False

        return True

    def __tabulate(self, serialize_data: bool = False):
        return (
            self.id,
            self.url,
            self.group,
            self.depth,
            self.spider,
            self.priority,
            self.data
            if not serialize_data
            else (
                json.dumps(self.data, ensure_ascii=False)
                if self.data is not None
                else None
            ),
            self.parent,
        )

    def __getstate__(self):
        return self.__tabulate()

    def __csv_row__(self):
        return self.__tabulate(serialize_data=True)

    def __setstate__(self, state):
        (
            self.id,
            self.url,
            self.group,
            self.depth,
            self.spider,
            self.priority,
            self.data,
            self.parent,
        ) = state

    def __repr__(self):
        return format_repr(
            self,
            (
                "id",
                "url",
                "depth",
                "spider",
                ("priority", self.priority or None),
                "data",
                "parent",
            ),
            conditionals=("data", "spider", "parent", "group", "priority"),
        )


class CrawlResult(Generic[CrawlJobDataType, CrawlResultDataType]):
    __slots__ = ("job", "data", "error", "response", "degree")

    FIELDNAMES = [
        "id",
        "parent",
        "spider",
        "depth",
        "url",
        "resolved_url",
        "error",
        "status",
        "mimetype",
        "degree",
        "body_size",
        "encoding",
    ]

    job: CrawlJob[CrawlJobDataType]
    data: Optional[CrawlResultDataType]
    error: Optional[Exception]
    response: Optional[Response]
    degree: int

    @classmethod
    def fieldnames(cls, singular: bool = False) -> List[str]:
        return (
            cls.FIELDNAMES
            if not singular
            else [f for f in cls.FIELDNAMES if f != "spider"]
        )

    def __init__(self, job: CrawlJob[CrawlJobDataType]):
        self.job = job
        self.data = None
        self.error = None
        self.response = None
        self.degree = 0

    @property
    def url(self) -> str:
        return self.job.url

    @property
    def depth(self) -> int:
        return self.job.depth

    @property
    def spider(self) -> Optional[str]:
        return self.job.spider

    @property
    def error_code(self) -> Optional[str]:
        return serialize_error_as_slug(self.error) if self.error else None

    def __csv_row__(self):
        job = self.job

        row = [job.id, job.parent]

        if job.spider is not None:
            row.append(job.spider)

        row.extend(
            [
                job.depth,
                job.url,
                self.response.end_url if self.response else None,
                self.error_code,
                self.response.status if self.response else None,
                self.response.mimetype if self.response else None,
                self.degree,
                len(self.response) if self.response else None,
                self.response.encoding if self.response else None,
            ]
        )

        return row

    def as_csv_row(self):
        return self.__csv_row__()

    def __repr__(self) -> str:
        encoding = self.response.encoding if self.response else None

        if encoding and normalize_encoding(encoding) == "utf8":
            encoding = None

        return format_repr(
            self,
            attributes=(
                (
                    "url",
                    "depth",
                    "spider",
                    ("error", self.error_code),
                    ("status", self.response.status if self.response else None),
                    ("degree", self.degree if self.error is None else None),
                    (
                        "dtype",
                        type(self.data).__name__ if self.data is not None else None,
                    ),
                    ("size", self.response.human_size if self.response else None),
                    ("mimetype", self.response.mimetype if self.response else None),
                    ("encoding", encoding),
                )
            ),
            conditionals=(
                "spider",
                "error",
                "status",
                "degree",
                "dtype",
                "size",
                "mimetype",
                "encoding",
            ),
        )


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

    @property
    def error_code(self) -> str:
        return serialize_error_as_slug(self.error)


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

    @property
    def error_code(self) -> None:
        return None


AnyCrawlResult = Union[
    ErroredCrawlResult[CrawlJobDataType],
    SuccessfulCrawlResult[CrawlJobDataType, CrawlResultDataType],
]
