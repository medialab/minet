from typing import List, Optional, Dict, Tuple, Iterable
from datetime import datetime

from dataclasses import dataclass
from casanova import TabularRecord
from ebbe import getpath


@dataclass
class RedditPost(TabularRecord):
    title: str
    url: str
    author: str
    author_text: Optional[str]
    upvote: str
    number_comments: int
    published_date: str
    link: Optional[str]


@dataclass
class RedditComment(TabularRecord):
    # url: str
    # author: str
    id: str
    parent: str
    # points: Optional[str]
    # published_date: str
    comment: str




