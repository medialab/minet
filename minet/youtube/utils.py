# =============================================================================
# Minet Youtube Utils
# =============================================================================
#
# Miscellaneous helper functions related to the Youtube API.
#
from typing import Optional

from pytz import timezone
from datetime import datetime
from ural import is_url
from ural.youtube import (
    is_youtube_video_id,
    is_youtube_channel_id,
    extract_video_id_from_youtube_url,
    parse_youtube_url,
    YoutubeChannel,
)


def seconds_to_midnight_pacific_time() -> int:
    now_utc = timezone("utc").localize(datetime.utcnow())
    pacific_time = now_utc.astimezone(timezone("US/Pacific")).replace(tzinfo=None)
    midnight_pacific = datetime.combine(pacific_time, datetime.min.time())

    return (midnight_pacific - pacific_time).seconds


def ensure_video_id(target):
    if is_youtube_video_id(target):
        return target

    return extract_video_id_from_youtube_url(target)


def ensure_channel_id(target: str) -> Optional[str]:
    if is_youtube_channel_id(target):
        return target

    if not is_url(target):
        return None

    parsed = parse_youtube_url(target)

    if parsed is None or not isinstance(parsed, YoutubeChannel):
        return None

    if parsed.id:
        return parsed.id

    return None


def get_channel_main_playlist_id(channel_id: str) -> str:
    return "UU" + channel_id[2:]
