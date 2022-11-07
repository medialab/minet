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
    extract_hashtags,
    extract_handles,
    short_code_to_url,
)
from minet.utils import timestamp_to_isoformat

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
        hashtags = "|".join(extract_hashtags(text))
        mentioned_names = "|".join(extract_handles(text))

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
        hashtags = "|".join(extract_hashtags(text))
        mentioned_names = "|".join(extract_handles(text))

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


def format_user(item):

    row = InstagramUserFollow(
        item.get("pk"),
        item.get("username"),
        item.get("full_name"),
        item.get("is_private"),
        item.get("profile_pic_url"),
        item.get("profile_pic_id"),
        item.get("is_verified"),
        item.get("has_anonymous_profile_picture"),
        item.get("has_highlight_reels"),
        item.get("account_badges"),
        item.get("similar_user_id"),
        item.get("latest_reel_media"),
        item.get("is_favorite"),
    )

    return row
