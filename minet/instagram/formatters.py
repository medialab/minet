# =============================================================================
# Minet Instagram Formatters
# =============================================================================
#
# Various data formatters for Instagram data.
#
from casanova import namedrecord
from ebbe import getpath

from minet.instagram.constants import (
    INSTAGRAM_HASHTAG_POST_CSV_HEADERS,
    INSTAGRAM_USER_POST_CSV_HEADERS,
    INSTAGRAM_MEDIA_TYPE,
)
from minet.instagram.utils import extract_from_text

InstagramHashtagPost = namedrecord(
    "InstagramHashtagPost",
    INSTAGRAM_HASHTAG_POST_CSV_HEADERS,
    boolean=[
        "comments_disabled",
    ],
)

InstagramUserPost = namedrecord(
    "InstagramUserPost",
    INSTAGRAM_USER_POST_CSV_HEADERS,
    boolean=[
        "like_and_view_counts_disabled",
    ],
)


def format_hashtag_post(item):

    hashtags = "|".join(
        extract_from_text(
            getpath(item, ["edge_media_to_caption", "edges", 0, "node", "text"]), "#"
        )
    )

    mentioned_names = "|".join(
        extract_from_text(
            getpath(item, ["edge_media_to_caption", "edges", 0, "node", "text"]), "@"
        )
    )

    row = InstagramHashtagPost(
        item["id"],
        item["__typename"],
        item["shortcode"],
        getpath(item, ["edge_media_to_caption", "edges", 0, "node", "text"]),
        hashtags,
        mentioned_names,
        item["edge_liked_by"]["count"],
        item["comments_disabled"],
        item["edge_media_to_comment"]["count"],
        item["edge_media_preview_like"]["count"],
        item.get("video_view_count"),
        item["owner"]["id"],
        item["taken_at_timestamp"],
        item["accessibility_caption"],
        item["display_url"],
    )

    return row


def format_user_post(item):

    media_type = INSTAGRAM_MEDIA_TYPE.get(item["media_type"])
    if media_type is None:
        media_type = item["media_type"]

    hashtags = "|".join(
        extract_from_text(
            getpath(item, ["edge_media_to_caption", "edges", 0, "node", "text"]), "#"
        )
    )

    mentioned_names = "|".join(
        extract_from_text(
            getpath(item, ["edge_media_to_caption", "edges", 0, "node", "text"]), "@"
        )
    )

    row = InstagramUserPost(
        item["id"],
        media_type,
        item["code"],
        getpath(item, ["caption", "text"]),
        hashtags,
        mentioned_names,
        item["like_and_view_counts_disabled"],
        item["like_count"],
        item["comment_count"],
        item.get("view_count"),
        item.get("title"),
        item.get("video_duration"),
        item["taken_at"],
    )

    return row
