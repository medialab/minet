# =============================================================================
# Minet Tiktok Formatters
# =============================================================================
#
# Various data formatters for Tiktok data.
#
from casanova import namedrecord
from ebbe import getpath
from minet.utils import timestamp_to_isoformat

from minet.tiktok.constants import (
    TIKTOK_VIDEO_CSV_HEADERS,
)

TiktokVideo = namedrecord(
    "TiktokVideo",
    TIKTOK_VIDEO_CSV_HEADERS,
    boolean=[
        "original_item",
        "author_verified",
        "author_secret",
        "music_original",
        "duet_enabled",
        "stitch_enabled",
        "share_enabled",
        "is_ad",
    ],
    plural=[
        "challenges_titles",
        "challenges_descriptions",
        "stickers_texts",
        "effect_stickers_names",
    ],
)


def format_video(item):

    challenges_titles = []
    challenges_descs = []
    stickers_texts = []
    effect_stickers_names = []

    challenges = item.get("challenges")
    if challenges:
        for challenge in challenges:
            challenges_titles.append(challenge.get("title"))
            challenges_descs.append(challenge.get("desc"))

    stickers = item.get("stickersOnItem")
    if stickers:
        for sticker in stickers:
            stickers_texts.append(" ".join(sticker.get("stickerText")))

    effects = item.get("effectStickers")
    if effects:
        for effect in effects:
            effect_stickers_names.append(effect.get("name"))

    duet_from_id = getpath(item, ["duetInfo", "duetFromId"])

    if duet_from_id == "0":
        duet_from_id = None
        duet_from_user_id = None
        duet_from_user_name = None
        duet_from_user_is_commerce = None
    else:
        for text in getpath(item, ["textExtra"]):
            if text["awemeId"] == duet_from_id:
                duet_from_user_id = text["userId"]
                duet_from_user_name = text["userUniqueId"]
                duet_from_user_is_commerce = text["isCommerce"]

    row = TiktokVideo(
        item.get("id"),
        item.get("desc"),
        item.get("createTime"),
        timestamp_to_isoformat(item.get("createTime")),
        item.get("originalItem"),
        getpath(item, ["video", "id"]),
        getpath(item, ["video", "height"]),
        getpath(item, ["video", "width"]),
        getpath(item, ["video", "duration"]),
        getpath(item, ["video", "ratio"]),
        getpath(item, ["video", "cover"]),
        getpath(item, ["video", "originCover"]),
        getpath(item, ["video", "dynamicCover"]),
        # Access denied
        # getpath(item, ["video", "downloadAddr"]),
        getpath(item, ["video", "reflowCover"]),
        getpath(item, ["video", "bitrate"]),
        getpath(item, ["video", "format"]),
        getpath(item, ["video", "videoQuality"]),
        getpath(item, ["author", "id"]),
        getpath(item, ["author", "uniqueId"]),
        getpath(item, ["author", "nickname"]),
        getpath(item, ["author", "avatarLarger"]),
        getpath(item, ["author", "signature"]),
        getpath(item, ["author", "verified"]),
        getpath(item, ["author", "secret"]),
        getpath(item, ["authorStats", "followingCount"]),
        getpath(item, ["authorStats", "followerCount"]),
        getpath(item, ["authorStats", "heartCount"]),
        getpath(item, ["authorStats", "videoCount"]),
        getpath(item, ["authorStats", "diggCount"]),
        getpath(item, ["music", "id"]),
        getpath(item, ["music", "title"]),
        getpath(item, ["music", "authorName"]),
        getpath(item, ["music", "original"]),
        getpath(item, ["music", "playUrl"]),
        getpath(item, ["music", "duration"]),
        getpath(item, ["music", "album"]),
        getpath(item, ["stats", "diggCount"]),
        getpath(item, ["stats", "shareCount"]),
        getpath(item, ["stats", "commentCount"]),
        getpath(item, ["stats", "playCount"]),
        duet_from_id,
        duet_from_user_id,
        duet_from_user_name,
        duet_from_user_is_commerce,
        challenges_titles,
        challenges_descs,
        stickers_texts,
        effect_stickers_names,
        item.get("duetEnabled"),
        item.get("stitchEnabled"),
        item.get("shareEnabled"),
        item.get("isAd"),
    )

    return row
