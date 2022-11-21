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
    INSTAGRAM_USER_CSV_HEADERS,
)
from minet.instagram.utils import (
    extract_hashtags,
    extract_handles,
    short_code_to_url,
)
from minet.utils import timestamp_to_isoformat

INSTAGRAM_PATH_TO_MEDIA_IMAGE = ["image_versions2", "candidates", 0, "url"]
INSTAGRAM_PATH_TO_MEDIA_VIDEO = ["video_versions", 0, "url"]

InstagramHashtagPost = namedrecord(
    "InstagramHashtagPost",
    INSTAGRAM_HASHTAG_POST_CSV_HEADERS,
    boolean=[
        "comments_disabled",
    ],
    plural=["hashtags", "mentioned_names"],
)

InstagramUserPost = namedrecord(
    "InstagramUserPost",
    INSTAGRAM_USER_POST_CSV_HEADERS,
    boolean=["like_and_view_counts_disabled", "is_verified"],
    plural=[
        "medias_type",
        "medias_url",
        "usertags_medias",
        "mentioned_names",
        "hashtags",
    ],
)

InstagramUser = namedrecord(
    "InstagramUser",
    INSTAGRAM_USER_CSV_HEADERS,
    boolean=[
        "is_private",
        "is_verified",
        "has_anonymous_profile_picture",
        "has_highlight_reels",
        "is_favorite",
    ],
)


def get_usertags(item, usertags):
    users = getpath(item, ["usertags", "in"])
    if not users:
        return
    for user in users:
        username = getpath(user, ["user", "username"])
        if username not in usertags:
            usertags.append(username)


def format_hashtag_post(item):

    text = getpath(item, ["edge_media_to_caption", "edges", 0, "node", "text"])

    hashtags = []
    mentioned_names = []

    if text:
        hashtags = extract_hashtags(text)
        mentioned_names = extract_handles(text)

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
        short_code_to_url(item["code"]) + "/media/?size=l",
    )

    return row


def format_user_post(item):

    media_type = INSTAGRAM_MEDIA_TYPE.get(item["media_type"])
    if media_type is None:
        media_type = item["media_type"]

    text = getpath(item, ["caption", "text"])

    hashtags = []
    mentioned_names = []

    if text:
        hashtags = extract_hashtags(text)
        mentioned_names = extract_handles(text)

    medias_url = []
    medias_type = []
    usertags_medias = []

    if media_type == "GraphSidecar":
        carousel = getpath(item, ["carousel_media"])
        for media in carousel:
            medias_type.append(INSTAGRAM_MEDIA_TYPE.get(getpath(media, ["media_type"])))

            if medias_type[-1] == "GraphImage":
                medias_url.append(getpath(media, INSTAGRAM_PATH_TO_MEDIA_IMAGE))
                get_usertags(media, usertags_medias)

            elif medias_type[-1] == "GraphVideo":
                medias_url.append(getpath(media, INSTAGRAM_PATH_TO_MEDIA_VIDEO))
                get_usertags(media, usertags_medias)

    elif media_type == "GraphImage":
        medias_type.append("GraphImage")
        medias_url.append(getpath(item, INSTAGRAM_PATH_TO_MEDIA_IMAGE))
        get_usertags(item, usertags_medias)

    elif media_type == "GraphVideo":
        medias_type.append("GraphVideo")
        medias_url.append(getpath(item, INSTAGRAM_PATH_TO_MEDIA_VIDEO))
        get_usertags(item, usertags_medias)

    row = InstagramUserPost(
        getpath(item, ["user", "username"]),
        getpath(item, ["user", "full_name"]),
        getpath(item, ["user", "is_verified"]),
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
        short_code_to_url(item["code"]) + "media/?size=l",
        medias_type,
        medias_url,
        usertags_medias,
        item["taken_at"],
        timestamp_to_isoformat(item["taken_at"]),
    )

    return row


def format_user(item):

    row = InstagramUser(
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
