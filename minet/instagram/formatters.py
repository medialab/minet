# =============================================================================
# Minet Instagram Formatters
# =============================================================================
#
# Various data formatters for Instagram data.
#
from casanova import namedrecord
from ebbe import getpath

from minet.instagram.constants import (
    INSTAGRAM_COMMENT_CSV_HEADERS,
    INSTAGRAM_HASHTAG_POST_CSV_HEADERS,
    INSTAGRAM_POST_CSV_HEADERS,
    INSTAGRAM_MEDIA_TYPE,
    INSTAGRAM_USER_CSV_HEADERS,
    INSTAGRAM_USER_INFO_CSV_HEADERS,
)
from minet.instagram.utils import (
    extract_hashtags,
    extract_handles,
    short_code_to_url,
)
from minet.dates import timestamp_to_isoformat

INSTAGRAM_PATH_TO_MEDIA_IMAGE = ["image_versions2", "candidates", 0, "url"]
INSTAGRAM_PATH_TO_MEDIA_VIDEO = ["video_versions", 0, "url"]

InstagramComment = namedrecord(
    "InstagramComment",
    INSTAGRAM_COMMENT_CSV_HEADERS,
    boolean=[
        "has_translation",
        "is_liked_by_media_owner",
        "user_is_private",
        "user_is_mentionable",
        "user_is_verified",
    ],
    plural=["hashtags", "mentioned_names"],
)

InstagramHashtagPost = namedrecord(
    "InstagramHashtagPost",
    INSTAGRAM_HASHTAG_POST_CSV_HEADERS,
    boolean=[
        "comments_disabled",
    ],
    plural=["hashtags", "mentioned_names"],
)

InstagramPost = namedrecord(
    "InstagramPost",
    INSTAGRAM_POST_CSV_HEADERS,
    boolean=["like_and_view_counts_disabled", "is_verified"],
    plural=[
        "medias_type",
        "medias_url",
        "usertags_medias",
        "mentioned_names",
        "hashtags",
        "coauthor_usernames",
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

InstagramUserInfo = namedrecord(
    "InstagramUserInfo",
    INSTAGRAM_USER_INFO_CSV_HEADERS,
    boolean=[
        "is_private",
        "is_verified",
        "hide_like_and_view_counts",
        "has_ar_effects",
        "has_clips",
        "has_guides",
        "has_channel",
        "is_business_account",
        "is_professional_account",
        "is_supervision_enabled",
        "is_guardian_of_viewer",
        "is_supervised_by_viewer",
        "is_supervised_user",
        "is_joined_recently",
    ],
    plural=[
        "bio_links_title",
        "bio_links_url",
        "biography_with_username",
        "biography_with_hashtag",
        "pronouns",
    ],
)


def get_usertags(item):
    users = getpath(item, ["usertags", "in"])
    usertags = set()
    if not users:
        return usertags
    for user in users:
        username = getpath(user, ["user", "username"])
        usertags.add(username)
    return usertags


def format_comment(comment):
    text = comment.get("text")

    hashtags = []
    mentioned_names = []

    if comment.get("text"):
        hashtags = extract_hashtags(text)
        mentioned_names = extract_handles(text)

    row = InstagramComment(
        comment.get("pk"),
        comment.get("comment_index"),
        comment.get("parent_comment_id"),
        comment.get("child_comment_index"),
        comment.get("text"),
        hashtags,
        mentioned_names,
        comment.get("has_translation", False),
        comment.get("comment_like_count"),
        comment.get("is_liked_by_media_owner"),
        comment.get("child_comment_count"),
        comment.get("created_at_utc"),
        timestamp_to_isoformat(comment.get("created_at_utc")),
        getpath(comment, ["user", "username"]),
        comment.get("user_id"),
        getpath(comment, ["user", "full_name"]),
        getpath(comment, ["user", "is_private"]),
        getpath(comment, ["user", "is_mentionable"]),
        getpath(comment, ["user", "is_verified"]),
        getpath(comment, ["user", "profile_pic_id"]),
        getpath(comment, ["user", "profile_pic_url"]),
        getpath(comment, ["user", "fbid_v2"]),
    )

    return row


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
        short_code_to_url(item["shortcode"]) + "media/?size=l",
    )

    return row


def format_post(item):
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
    usertags_medias = set()

    if media_type == "GraphSidecar":
        carousel = getpath(item, ["carousel_media"])
        for media in carousel:
            medias_type.append(INSTAGRAM_MEDIA_TYPE.get(getpath(media, ["media_type"])))

            if medias_type[-1] == "GraphImage":
                medias_url.append(getpath(media, INSTAGRAM_PATH_TO_MEDIA_IMAGE))
                item_usertags = get_usertags(media)
                usertags_medias = usertags_medias.union(item_usertags)

            elif medias_type[-1] == "GraphVideo":
                medias_url.append(getpath(media, INSTAGRAM_PATH_TO_MEDIA_VIDEO))
                item_usertags = get_usertags(media)
                usertags_medias = usertags_medias.union(item_usertags)

    elif media_type == "GraphImage":
        medias_type.append("GraphImage")
        medias_url.append(getpath(item, INSTAGRAM_PATH_TO_MEDIA_IMAGE))
        item_usertags = get_usertags(item)
        usertags_medias = usertags_medias.union(item_usertags)

    elif media_type == "GraphVideo":
        medias_type.append("GraphVideo")
        medias_url.append(getpath(item, INSTAGRAM_PATH_TO_MEDIA_VIDEO))
        item_usertags = get_usertags(item)
        usertags_medias = usertags_medias.union(item_usertags)

    coauthor_usernames = set()

    for other_user in item.get("coauthor_producers", []) + item.get(
        "invited_coauthor_producers", []
    ):
        coauthor_username = other_user.get("username")

        if coauthor_username is not None:
            coauthor_usernames.add(coauthor_username)

    row = InstagramPost(
        getpath(item, ["user", "username"]),
        getpath(item, ["user", "full_name"]),
        getpath(item, ["user", "is_verified"]),
        item["pk"],
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
        list(coauthor_usernames),
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


def format_user_info(user):
    bio_links_title = []
    bio_links_url = []
    biography_with_username = []
    biography_with_hashtag = []

    bio_links = user.get("bio_links")
    if bio_links:
        for link in bio_links:
            bio_links_title.append(link.get("title"))
            bio_links_url.append(link.get("url"))

    biography_with_entities = getpath(user, ["biography_with_entities", "entities"])

    if biography_with_entities:
        for entity in biography_with_entities:
            username = getpath(entity, ["user", "username"])
            if username:
                biography_with_username.append(username)

            hashtag = getpath(entity, ["user", "hashtag"])
            if hashtag:
                biography_with_hashtag.append(hashtag)

    pronouns = user.get("pronouns")

    row = InstagramUserInfo(
        user.get("username"),
        user.get("id"),
        user.get("full_name"),
        user.get("profile_pic_url_hd"),
        user.get("is_private"),
        user.get("is_verified"),
        user.get("biography"),
        bio_links_title,
        bio_links_url,
        biography_with_username,
        biography_with_hashtag,
        getpath(user, ["edge_followed_by", "count"]),
        getpath(user, ["edge_follow", "count"]),
        user.get("hide_like_and_view_counts"),
        pronouns,
        user.get("has_ar_effects"),
        user.get("has_clips"),
        user.get("has_guides"),
        user.get("has_channel"),
        user.get("is_business_account"),
        user.get("is_professional_account"),
        user.get("is_supervision_enabled"),
        user.get("is_guardian_of_viewer"),
        user.get("is_supervised_by_viewer"),
        user.get("is_supervised_user"),
        user.get("guardian_id"),
        user.get("is_joined_recently"),
        user.get("business_category_name"),
        user.get("category_name"),
        user.get("connected_fb_page"),
    )

    return row
