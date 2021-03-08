# =============================================================================
# Minet Youtube Utils
# =============================================================================
#
# Miscellaneous helper functions related to the Youtube API.
#
from pytz import timezone
from datetime import datetime
from ural.youtube import is_youtube_video_id, extract_video_id_from_youtube_url


def seconds_to_midnight_pacific_time():
    now_utc = timezone('utc').localize(datetime.utcnow())
    pacific_time = now_utc.astimezone(timezone('US/Pacific')).replace(tzinfo=None)
    midnight_pacific = datetime.combine(pacific_time, datetime.min.time())

    return (midnight_pacific - pacific_time).seconds


def ensure_video_id(target):
    if is_youtube_video_id(target):
        return target

    return extract_video_id_from_youtube_url(target)
