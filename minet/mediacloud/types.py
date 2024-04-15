from typing import Optional, List

from dataclasses import dataclass
from casanova import TabularRecord

from minet.mediacloud.utils import explode_tags


@dataclass
class MediacloudTopicStory(TabularRecord):
    guid: str
    stories_id: str
    title: str
    url: str
    language: str
    media_id: str
    media_name: str
    collect_date: str
    publish_date: str
    date_is_reliable: bool
    facebook_share_count: int
    full_text_rss: bool
    inlink_count: int
    outlink_count: int
    media_inlink_count: int
    post_count: int
    snapshots_id: str
    timespans_id: str
    next_link_id: Optional[str]

    @classmethod
    def from_payload(cls, payload, next_link_id=None) -> "MediacloudTopicStory":
        return cls(
            payload["guid"],
            payload["stories_id"],
            payload["title"],
            payload["url"],
            payload["language"],
            payload["media_id"],
            payload["media_name"],
            payload["collect_date"],
            payload["publish_date"],
            payload["date_is_reliable"],
            payload["facebook_share_count"],
            bool(payload["full_text_rss"]),
            payload["inlink_count"],
            payload["outlink_count"],
            payload["media_inlink_count"],
            payload["post_count"],
            payload["snapshots_id"],
            payload["timespans_id"],
            next_link_id,
        )


@dataclass
class MediacloudStory(TabularRecord):
    guid: str
    stories_id: str
    processed_stories_id: str
    title: str
    url: str
    language: str
    collect_date: str
    publish_date: str
    media_id: str
    media_name: str
    media_url: str
    tags: List[str]
    tag_sets: List[str]
    tags_ids: List[str]
    tag_sets_ids: List[str]

    @classmethod
    def from_payload(cls, payload) -> "MediacloudStory":
        tags = payload.get("payload_tags")

        return cls(
            payload["guid"],
            payload["stories_id"],
            payload["processed_stories_id"],
            payload["title"],
            payload["url"],
            payload["language"],
            payload["collect_date"],
            payload["publish_date"],
            payload["media_id"],
            payload["media_name"],
            payload["media_url"],
            *explode_tags(tags),
        )


@dataclass
class MediacloudMedia(TabularRecord):
    media_id: str
    media_name: str
    media_url: str
    is_healthy: bool
    is_monitored: bool
    public_notes: str
    num_stories_90: int
    num_sentences_90: int
    start_date: str
    tags: List[str]
    tag_sets: List[str]
    tags_ids: List[str]
    tag_sets_ids: List[str]

    @classmethod
    def from_payload(cls, payload) -> "MediacloudMedia":
        tags = payload.get("media_source_tags")

        return cls(
            payload["media_id"],
            payload["name"],
            payload["url"],
            payload["is_healthy"],
            payload["is_monitored"],
            payload.get("public_notes"),
            payload["num_stories_90"],
            payload["num_sentences_90"],
            payload["start_date"],
            *explode_tags(tags),
        )


@dataclass
class MediacloudFeed(TabularRecord):
    name: str
    url: str
    feeds_id: str
    type: str
    media_id: str
    active: bool
    last_attempted_download_time: float
    last_new_story_time: float
    last_successful_download_time: float

    @classmethod
    def from_payload(cls, payload) -> "MediacloudFeed":
        return cls(
            payload["name"],
            payload["url"],
            payload["payloads_id"],
            payload["type"],
            payload["media_id"],
            payload["active"],
            payload.get("last_attempted_download_time"),
            payload.get("last_new_story_time"),
            payload.get("last_successful_download_time"),
        )
