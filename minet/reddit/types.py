from typing import Optional

from dataclasses import dataclass
from casanova import TabularRecord


@dataclass
class RedditPost(TabularRecord):
    title: str
    url: str
    author: str
    author_text: Optional[str]
    points: str
    raw_number_comments: str
    number_comments: int
    published_date: str
    edited_date: str
    external_link: Optional[str]
    error: str


@dataclass
class RedditComment(TabularRecord):
    comment_url: str
    author: str
    id: str
    parent: Optional[str]
    points: Optional[str]
    published_date: Optional[str]
    edited_date: Optional[str]
    comment: str
    error: Optional[str]


@dataclass
class RedditUserPost(TabularRecord):
    title: str
    url: str
    author_text: str
    points: str
    raw_number_comments: str
    number_comments: int
    published_date: str
    edited_date: str
    external_link: str
    subreddit: str
    error: str


@dataclass
class RedditUserComment(TabularRecord):
    post_title: str
    post_url: str
    post_author: str
    post_subreddit: str
    points: str
    published_date: Optional[str]
    edited_date: Optional[str]
    text: str
    link: str
    comment_url: str
    error: Optional[str]
