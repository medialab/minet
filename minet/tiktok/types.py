from typing import Optional, List

from dataclasses import dataclass
from casanova import TabularRecord
from ebbe import getpath

from minet.dates import timestamp_to_isoformat
from minet.tiktok.constants import TIKTOK_COMMERCIAL_CONTENTS_LABELS


@dataclass
class TiktokVideo(TabularRecord):
    id: str
    description: str
    timestamp: int
    utc_time: str
    original_item: bool
    video_id: str
    video_height: int
    video_width: int
    video_duration: int
    video_ratio: str
    video_cover: str
    video_origin_cover: str
    video_dynamic_cover: str
    video_reflow_cover: str
    video_bitrate: int
    video_format: str
    video_quality: str
    author_id: str
    author_unique_id: str
    author_nickname: str
    author_avatar: str
    author_signature: str
    author_verified: bool
    author_secret: bool
    author_following_count: int
    author_follower_count: int
    author_heart_count: int
    author_video_count: int
    author_digg_count: int
    music_id: str
    music_title: str
    music_author_name: str
    music_original: bool
    music_play_url: str
    music_duration: int
    music_album: Optional[str]
    digg_count: int
    share_count: int
    comment_count: int
    play_count: int
    duet_from_video_id: Optional[str]
    duet_from_user_id: Optional[str]
    duet_from_user_name: Optional[str]
    duet_from_user_is_commerce: Optional[bool]
    challenges_titles: List[str]
    challenges_descriptions: List[str]
    stickers_texts: List[str]
    effect_stickers_names: List[str]
    duet_enabled: bool
    stitch_enabled: bool
    share_enabled: bool
    is_ad: bool

    @classmethod
    def from_payload(cls, payload) -> "TiktokVideo":
        challenges_titles = []
        challenges_descs = []
        stickers_texts = []
        effect_stickers_names = []

        challenges = payload.get("challenges")
        if challenges:
            for challenge in challenges:
                challenges_titles.append(challenge.get("title"))
                challenges_descs.append(challenge.get("desc"))

        stickers = payload.get("stickersOnItem")
        if stickers:
            for sticker in stickers:
                stickers_texts.append(" ".join(sticker.get("stickerText")))

        effects = payload.get("effectStickers")
        if effects:
            for effect in effects:
                effect_stickers_names.append(effect.get("name"))

        duet_from_id = getpath(payload, ["duetInfo", "duetFromId"])
        duet_from_user_id = None
        duet_from_user_name = None
        duet_from_user_is_commerce = None

        if duet_from_id == "0":
            duet_from_id = None
            duet_from_user_id = None
            duet_from_user_name = None
            duet_from_user_is_commerce = None
        else:
            for text in getpath(payload, ["textExtra"]):
                if text["awemeId"] == duet_from_id:
                    duet_from_user_id = text["userId"]
                    duet_from_user_name = text["userUniqueId"]
                    duet_from_user_is_commerce = text["isCommerce"]

        return cls(
            payload.get("id"),
            payload.get("desc"),
            payload.get("createTime"),
            timestamp_to_isoformat(payload.get("createTime")),
            payload.get("originalItem"),
            getpath(payload, ["video", "id"]),
            getpath(payload, ["video", "height"]),
            getpath(payload, ["video", "width"]),
            getpath(payload, ["video", "duration"]),
            getpath(payload, ["video", "ratio"]),
            getpath(payload, ["video", "cover"]),
            getpath(payload, ["video", "originCover"]),
            getpath(payload, ["video", "dynamicCover"]),
            getpath(payload, ["video", "reflowCover"]),
            getpath(payload, ["video", "bitrate"]),
            getpath(payload, ["video", "format"]),
            getpath(payload, ["video", "videoQuality"]),
            getpath(payload, ["author", "id"]),
            getpath(payload, ["author", "uniqueId"]),
            getpath(payload, ["author", "nickname"]),
            getpath(payload, ["author", "avatarLarger"]),
            getpath(payload, ["author", "signature"]),
            getpath(payload, ["author", "verified"]),
            getpath(payload, ["author", "secret"]),
            getpath(payload, ["authorStats", "followingCount"]),
            getpath(payload, ["authorStats", "followerCount"]),
            getpath(payload, ["authorStats", "heartCount"]),
            getpath(payload, ["authorStats", "videoCount"]),
            getpath(payload, ["authorStats", "diggCount"]),
            getpath(payload, ["music", "id"]),
            getpath(payload, ["music", "title"]),
            getpath(payload, ["music", "authorName"]),
            getpath(payload, ["music", "original"]),
            getpath(payload, ["music", "playUrl"]),
            getpath(payload, ["music", "duration"]),
            getpath(payload, ["music", "album"]),
            getpath(payload, ["stats", "diggCount"]),
            getpath(payload, ["stats", "shareCount"]),
            getpath(payload, ["stats", "commentCount"]),
            getpath(payload, ["stats", "playCount"]),
            duet_from_id,
            duet_from_user_id,
            duet_from_user_name,
            duet_from_user_is_commerce,
            challenges_titles,
            challenges_descs,
            stickers_texts,
            effect_stickers_names,
            payload.get("duetEnabled"),
            payload.get("stitchEnabled"),
            payload.get("shareEnabled"),
            payload.get("isAd"),
        )


@dataclass
class TiktokCommercialContent(TabularRecord):
    id: str
    creator_username: str
    brand_names: List[str]
    create_date: str
    create_timestamp: int
    label: str
    video_cover_image_urls: List[str]
    video_urls: List[str]
    audit_status: Optional[int]
    show_mode: Optional[int]
    video_views: Optional[str]
    collected_via: str

    @classmethod
    def from_payload(cls, payload, collected_via) -> "TiktokCommercialContent":
        video_cover_image_urls = []
        video_urls = []

        videos = payload["videos"]

        timestamp = payload.get("create_timestamp")
        if timestamp is None:
            timestamp = payload["posted_time"]
        date = timestamp_to_isoformat(timestamp)

        if videos:
            for video in videos:
                video_cover_image_urls.append(
                    video.get("cover_image_url", video.get("cover_img"))
                )
                video_urls.append(video.get("url", video.get("video_url")))

        creator = payload["creator"]

        if "content_label" in payload:
            label = TIKTOK_COMMERCIAL_CONTENTS_LABELS[payload["content_label"]]
        else:
            label = payload.get("label")

        return cls(
            id=payload["id"],
            creator_username=creator["username"],
            brand_names=payload["brand_names"],
            create_date=date,
            create_timestamp=timestamp,
            label=label,
            video_cover_image_urls=video_cover_image_urls,
            video_urls=video_urls,
            audit_status=payload.get("audit_status"),
            show_mode=payload.get("show_mode"),
            video_views=payload.get("video_views"),
            collected_via=collected_via,
        )
