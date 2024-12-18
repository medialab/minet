from typing import List, Set

from dataclasses import dataclass
from casanova import TabularRecord
from ebbe import getpath

from minet.instagram.utils import (
    extract_hashtags,
    extract_handles,
    short_code_to_url,
)
from minet.instagram.constants import INSTAGRAM_MEDIA_TYPE
from minet.dates import timestamp_to_isoformat

INSTAGRAM_PATH_TO_MEDIA_IMAGE = ["image_versions2", "candidates", 0, "url"]
INSTAGRAM_PATH_TO_MEDIA_VIDEO = ["video_versions", 0, "url"]

# NOTE: we are lacking a great deal of optionals there...


@dataclass
class InstagramComment(TabularRecord):
    id: str
    index: str
    parent_id: str
    child_index: str
    text: str
    hashtags: List[str]
    mentioned_names: List[str]
    has_translation: bool
    comment_like_count: int
    is_liked_by_media_owner: bool
    child_comment_count: int
    created_at_utc: str
    utc_time: str
    username: str
    user_id: str
    user_full_name: str
    user_is_private: bool
    user_is_mentionable: bool
    user_is_verified: bool
    user_profile_pic_id: str
    user_profile_pic_url: str
    user_fbid_v2: str

    @classmethod
    def from_payload(cls, payload) -> "InstagramComment":
        text = payload.get("text")

        hashtags = []
        mentioned_names = []

        if payload.get("text"):
            hashtags = extract_hashtags(text)
            mentioned_names = extract_handles(text)

        return cls(
            payload.get("pk"),
            payload.get("comment_index"),
            payload.get("parent_comment_id"),
            payload.get("child_comment_index"),
            payload.get("text"),
            hashtags,
            mentioned_names,
            payload.get("has_translation", False),
            payload.get("comment_like_count"),
            payload.get("is_liked_by_media_owner"),
            payload.get("child_comment_count"),
            payload.get("created_at_utc"),
            timestamp_to_isoformat(payload.get("created_at_utc")),
            getpath(payload, ["user", "username"]),
            payload.get("user_id"),
            getpath(payload, ["user", "full_name"]),
            getpath(payload, ["user", "is_private"]),
            getpath(payload, ["user", "is_mentionable"]),
            getpath(payload, ["user", "is_verified"]),
            getpath(payload, ["user", "profile_pic_id"]),
            getpath(payload, ["user", "profile_pic_url"]),
            getpath(payload, ["user", "fbid_v2"]),
        )


@dataclass
class InstagramHashtagPost(TabularRecord):
    id: str
    media_type: str
    shortcode: str
    url: str
    caption: str
    hashtags: List[str]
    mentioned_names: List[str]
    liked_by_count: int
    comments_disabled: bool
    comment_count: int
    preview_like_count: int
    video_view_count: int
    owner_id: str
    taken_at_timestamp: str
    utc_time: str
    accessibility_caption: str
    display_url: str

    @classmethod
    def from_payload(cls, payload) -> "InstagramHashtagPost":
        text = getpath(payload, ["edge_media_to_caption", "edges", 0, "node", "text"])

        hashtags = []
        mentioned_names = []

        if text:
            hashtags = extract_hashtags(text)
            mentioned_names = extract_handles(text)

        return cls(
            payload["id"],
            payload["__typename"],
            payload["shortcode"],
            short_code_to_url(payload["shortcode"]),
            text,
            hashtags,
            mentioned_names,
            payload["edge_liked_by"]["count"],
            payload["comments_disabled"],
            payload["edge_media_to_comment"]["count"],
            payload["edge_media_preview_like"]["count"],
            payload.get("video_view_count"),
            payload["owner"]["id"],
            payload["taken_at_timestamp"],
            timestamp_to_isoformat(payload["taken_at_timestamp"]),
            payload["accessibility_caption"],
            short_code_to_url(payload["shortcode"]) + "media/?size=l",
        )


@dataclass
class InstagramLocationPost(TabularRecord):
    id: str
    is_video: str
    shortcode: str
    url: str
    caption: str
    hashtags: List[str]
    mentioned_names: List[str]
    liked_by_count: int
    comments_disabled: bool
    comment_count: int
    preview_like_count: int
    video_view_count: int
    owner_id: str
    taken_at_timestamp: str
    utc_time: str
    display_url: str

    @classmethod
    def from_payload(cls, payload) -> "InstagramLocationPost":
        text = getpath(payload, ["edge_media_to_caption", "edges", 0, "node", "text"])

        hashtags = []
        mentioned_names = []

        if text:
            hashtags = extract_hashtags(text)
            mentioned_names = extract_handles(text)

        return cls(
            payload["id"],
            payload["is_video"],
            payload["shortcode"],
            short_code_to_url(payload["shortcode"]),
            text,
            hashtags,
            mentioned_names,
            payload["edge_liked_by"]["count"],
            payload["comments_disabled"],
            payload["edge_media_to_comment"]["count"],
            payload["edge_media_preview_like"]["count"],
            payload.get("video_view_count"),
            payload["owner"]["id"],
            payload["taken_at_timestamp"],
            timestamp_to_isoformat(payload["taken_at_timestamp"]),
            short_code_to_url(payload["shortcode"]) + "media/?size=l",
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


@dataclass
class InstagramPost(TabularRecord):
    username: str
    full_name: str
    is_verified: bool
    id: str
    media_type: str
    shortcode: str
    url: str
    caption: str
    hashtags: List[str]
    mentioned_names: List[str]
    like_and_view_counts_disabled: bool
    like_count: int
    comment_count: int
    main_thumbnail_url: str
    medias_type: List[str]
    medias_url: List[str]
    usertags_medias: Set[str]
    taken_at_timestamp: str
    utc_time: str
    coauthor_usernames: List[str]

    @classmethod
    def from_payload(cls, payload) -> "InstagramPost":
        media_type = INSTAGRAM_MEDIA_TYPE.get(payload["media_type"])
        if media_type is None:
            media_type = payload["media_type"]

        text = getpath(payload, ["caption", "text"])

        hashtags = []
        mentioned_names = []

        if text:
            hashtags = extract_hashtags(text)
            mentioned_names = extract_handles(text)

        medias_url = []
        medias_type = []
        usertags_medias = set()

        if media_type == "GraphSidecar":
            carousel = getpath(payload, ["carousel_media"])
            for media in carousel:
                medias_type.append(
                    INSTAGRAM_MEDIA_TYPE.get(getpath(media, ["media_type"]))
                )

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
            medias_url.append(getpath(payload, INSTAGRAM_PATH_TO_MEDIA_IMAGE))
            item_usertags = get_usertags(payload)
            usertags_medias = usertags_medias.union(item_usertags)

        elif media_type == "GraphVideo":
            medias_type.append("GraphVideo")
            medias_url.append(getpath(payload, INSTAGRAM_PATH_TO_MEDIA_VIDEO))
            item_usertags = get_usertags(payload)
            usertags_medias = usertags_medias.union(item_usertags)

        coauthor_usernames = set()

        for other_user in payload.get("coauthor_producers", []) + payload.get(
            "invited_coauthor_producers", []
        ):
            coauthor_username = other_user.get("username")

            if coauthor_username is not None:
                coauthor_usernames.add(coauthor_username)

        return cls(
            getpath(payload, ["user", "username"]),
            getpath(payload, ["user", "full_name"]),
            getpath(payload, ["user", "is_verified"]),
            payload["pk"],
            media_type,
            payload["code"],
            short_code_to_url(payload["code"]),
            text,
            hashtags,
            mentioned_names,
            payload["like_and_view_counts_disabled"],
            payload["like_count"],
            payload["comment_count"],
            short_code_to_url(payload["code"]) + "media/?size=l",
            medias_type,
            medias_url,
            usertags_medias,
            payload["taken_at"],
            timestamp_to_isoformat(payload["taken_at"]),
            list(coauthor_usernames),
        )


@dataclass
class InstagramUser(TabularRecord):
    id: str
    username: str
    full_name: str
    is_private: bool
    profile_pic_url: str
    profile_pic_id: str
    is_verified: bool
    has_anonymous_profile_picture: str
    has_highlight_reels: bool
    account_badges: List[str]
    similar_user_id: str
    latest_reel_media: str
    is_favorite: bool

    @classmethod
    def from_payload(cls, payload) -> "InstagramUser":
        return cls(
            payload.get("pk"),
            payload.get("username"),
            payload.get("full_name"),
            payload.get("is_private"),
            payload.get("profile_pic_url"),
            payload.get("profile_pic_id"),
            payload.get("is_verified"),
            payload.get("has_anonymous_profile_picture"),
            payload.get("has_highlight_reels"),
            payload.get("account_badges"),
            payload.get("similar_user_id"),
            payload.get("latest_reel_media"),
            payload.get("is_favorite"),
        )


@dataclass
class InstagramUserInfo(TabularRecord):
    username: str
    id: str
    full_name: str
    profile_pic_url_hd: str
    is_private: bool
    is_verified: bool
    biography: str
    bio_links_title: List[str]
    bio_links_url: List[str]
    biography_with_username: List[str]
    biography_with_hashtag: List[str]
    follower_count: str
    follow_count: str
    hide_like_and_view_counts: bool
    pronouns: List[str]
    has_ar_effects: bool
    has_clips: bool
    has_guides: bool
    has_channel: bool
    is_business_account: bool
    is_professional_account: bool
    is_supervision_enabled: bool
    is_guardian_of_viewer: bool
    is_supervised_by_viewer: bool
    is_supervised_user: bool
    guardian_id: str
    is_joined_recently: str
    business_category_name: str
    category_name: str
    connected_fb_page: str

    @classmethod
    def from_payload(cls, payload) -> "InstagramUserInfo":
        bio_links_title = []
        bio_links_url = []
        biography_with_username = []
        biography_with_hashtag = []

        bio_links = payload.get("bio_links")
        if bio_links:
            for link in bio_links:
                bio_links_title.append(link.get("title"))
                bio_links_url.append(link.get("url"))

        biography_with_entities = getpath(
            payload, ["biography_with_entities", "entities"]
        )

        if biography_with_entities:
            for entity in biography_with_entities:
                username = getpath(entity, ["user", "username"])
                if username:
                    biography_with_username.append(username)

                hashtag = getpath(entity, ["user", "hashtag"])
                if hashtag:
                    biography_with_hashtag.append(hashtag)

        pronouns = payload.get("pronouns")

        return cls(
            payload.get("username"),
            payload.get("id"),
            payload.get("full_name"),
            payload.get("profile_pic_url_hd"),
            payload.get("is_private"),
            payload.get("is_verified"),
            payload.get("biography"),
            bio_links_title,
            bio_links_url,
            biography_with_username,
            biography_with_hashtag,
            getpath(payload, ["edge_followed_by", "count"]),
            getpath(payload, ["edge_follow", "count"]),
            payload.get("hide_like_and_view_counts"),
            pronouns,
            payload.get("has_ar_effects"),
            payload.get("has_clips"),
            payload.get("has_guides"),
            payload.get("has_channel"),
            payload.get("is_business_account"),
            payload.get("is_professional_account"),
            payload.get("is_supervision_enabled"),
            payload.get("is_guardian_of_viewer"),
            payload.get("is_supervised_by_viewer"),
            payload.get("is_supervised_user"),
            payload.get("guardian_id"),
            payload.get("is_joined_recently"),
            payload.get("business_category_name"),
            payload.get("category_name"),
            payload.get("connected_fb_page"),
        )
