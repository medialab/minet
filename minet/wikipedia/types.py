from minet.types import Literal

from dataclasses import dataclass
from casanova import TabularRecord

Granularity = Literal["daily", "monthly"]
Agent = Literal["user", "all-agents"]
Access = Literal["all-access", "mobile-web", "mobile-app"]


@dataclass
class WikipediaPageViewsItem(TabularRecord):
    project: str
    article: str
    granularity: Granularity
    timestamp: int
    access: Access
    agent: Agent
    views: int
