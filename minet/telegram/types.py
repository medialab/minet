from typing import List

from dataclasses import dataclass
from casanova import TabularRecord


@dataclass
class TelegramChannelInfos(TabularRecord):
    title: str
    name: str
    link: str
    img: str
    description: str
    nb_subscribers: str
    nb_photos: str
    nb_videos: str
    nb_files: str
    nb_links: str


@dataclass
class TelegramChannelMessages(TabularRecord):
    link_to_message: str
    could_be_displayed: bool
    user: str
    user_link: str
    user_img: str
    text: str
    nb_hashtags: int
    hashtags: List[str]
    is_reply_img: bool
    is_reply_user: bool
    is_reply_text: bool
    stickers: List[str]
    nb_photos: int
    photos: List[str]
    nb_videos: int
    videos: List[str]
    videos_times: List[str]
    nb_files: int
    nb_links: int
    links: List[str]
    link_img: str
    link_site: str
    link_title: str
    link_description: str
    views: int
    datetime: str
    edited: bool
