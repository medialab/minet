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
    INSTAGRAM_USER_FOLLOW_CSV_HEADERS,
)
from minet.instagram.utils import (
    extract_from_text,
    timestamp_to_isoformat,
    short_code_to_url,
)

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

InstagramUserFollow = namedrecord(
    "InstagramUserFollow",
    INSTAGRAM_USER_FOLLOW_CSV_HEADERS,
    boolean=[
        "is_private",
        "is_verified",
        "has_anonymous_profile_picture",
        "has_highlight_reels",
        "is_favorite",
    ],
)


def format_hashtag_post(item):

    text = getpath(item, ["edge_media_to_caption", "edges", 0, "node", "text"])

    hashtags = None
    mentioned_names = None

    if text:
        hashtags = "|".join(extract_from_text(text, "#"))
        mentioned_names = "|".join(extract_from_text(text, "@"))

    row = InstagramHashtagPost(
        item["id"],
        item["__typename"],
        item["shortcode"],
        short_code_to_url(item["shortcode"]),
        text,
        hashtags,
        mentioned_names,
        item["edge_liked_by"]["count"],
        item["comments_disabled"],
        item["edge_media_to_comment"]["count"],
        item["edge_media_preview_like"]["count"],
        item.get("video_view_count"),
        item["owner"]["id"],
        item["taken_at_timestamp"],
        timestamp_to_isoformat(item["taken_at_timestamp"]),
        item["accessibility_caption"],
        item["display_url"],
    )

    return row


def format_user_post(item):

    media_type = INSTAGRAM_MEDIA_TYPE.get(item["media_type"])
    if media_type is None:
        media_type = item["media_type"]

    text = getpath(item, ["caption", "text"])

    hashtags = None
    mentioned_names = None

    if text:
        hashtags = "|".join(extract_from_text(text, "#"))
        mentioned_names = "|".join(extract_from_text(text, "@"))

    row = InstagramUserPost(
        item["id"],
        media_type,
        item["code"],
        short_code_to_url(item["code"]),
        text,
        hashtags,
        mentioned_names,
        item["like_and_view_counts_disabled"],
        item["like_count"],
        item["comment_count"],
        item.get("view_count"),
        item.get("title"),
        item.get("video_duration"),
        item["taken_at"],
        timestamp_to_isoformat(item["taken_at"]),
    )

    return row


def format_user_follow(item):

    row = InstagramUserFollow(
        getpath(item, ["pk"]),
        getpath(item, ["username"]),
        getpath(item, ["full_name"]),
        getpath(item, ["is_private"]),
        getpath(item, ["profile_pic_url"]),
        getpath(item, ["profile_pic_id"]),
        getpath(item, ["is_verified"]),
        getpath(item, ["has_anonymous_profile_picture"]),
        getpath(item, ["has_highlight_reels"]),
        getpath(item, ["account_badges"]),
        getpath(item, ["similar_user_id"]),
        getpath(item, ["latest_reel_media"]),
        getpath(item, ["is_favorite"]),
    )

    return row
