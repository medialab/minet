# =============================================================================
# Minet YouTube Formatters
# =============================================================================
#
# Various data formatters for YouTube data.
#
from minet.utils import namedrecord
from minet.youtube.constants import YOUTUBE_VIDEO_CSV_HEADERS

YouTubeVideo = namedrecord(
    'YouTubeVideo',
    YOUTUBE_VIDEO_CSV_HEADERS,
    boolean=['has_caption']
)


def get_int(item, key):
    nb = item.get(key)

    if nb is not None:
        return int(nb)

    return nb


def format_video(item):
    snippet = item['snippet']
    stats = item['statistics']
    details = item['contentDetails']

    row = YouTubeVideo(
        item['id'],
        snippet['publishedAt'],
        snippet['channelId'],
        snippet['title'],
        snippet['description'],
        snippet['channelTitle'],
        get_int(stats, 'viewCount'),
        get_int(stats, 'likeCount'),
        get_int(stats, 'dislikeCount'),
        get_int(stats, 'favoriteCount'),
        get_int(stats, 'commentCount'),
        details['duration'],
        details['caption'] == 'true'
    )

    return row
