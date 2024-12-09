from typing import Optional

from dataclasses import dataclass
from casanova import TabularRecord


@dataclass
class RedditPost(TabularRecord):
    title: str
    url: str
    author: str
    author_text: Optional[str]
    upvote: int
    number_comments: int
    published_date: str
    link: Optional[str]


@dataclass
class RedditComment(TabularRecord):
    comment_url: str
    author: str
    id: str
    parent: str
    points: int
    published_date: str
    comment: str
