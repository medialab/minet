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
    scraped_number_comments: str
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
    parent: str
    points: str
    published_date: str
    edited_date: str
    comment: str
    error: str


@dataclass
class RedditUserPost(TabularRecord):
    title: str
    url: str
    author_text: str
    points: str
    scraped_number_comments: str
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
    points: int
    published_date: str
    edited_date: str
    text: str
    link: str
    comment_url: str
    error: str
