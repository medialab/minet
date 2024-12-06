from typing import Optional

from dataclasses import dataclass
from casanova import TabularRecord


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
