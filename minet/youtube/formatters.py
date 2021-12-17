# =============================================================================
# Minet YouTube Formatters
# =============================================================================
#
# Various data formatters for YouTube data.
#
from casanova import namedrecord
from ebbe import getpath

from minet.youtube.constants import (
    YOUTUBE_VIDEO_CSV_HEADERS,
    YOUTUBE_VIDEO_SNIPPET_CSV_HEADERS,
    YOUTUBE_COMMENT_CSV_HEADERS
)

YouTubeVideo = namedrecord(
    'YouTubeVideo',
    YOUTUBE_VIDEO_CSV_HEADERS,
    boolean=['has_caption']
)

YouTubeVideoSnippet = namedrecord(
    'YouTubeVideoSnippet',
    YOUTUBE_VIDEO_SNIPPET_CSV_HEADERS
)

YouTubeComment = namedrecord(
    'YoutubeComment',
    YOUTUBE_COMMENT_CSV_HEADERS
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
        # get_int(stats, 'dislikeCount'),
        # get_int(stats, 'favoriteCount'),
        get_int(stats, 'commentCount'),
        details['duration'],
        details['caption'] == 'true'
    )

    return row


def format_video_snippet(item):
    snippet = item['snippet']

    row = YouTubeVideoSnippet(
        item['id']['videoId'],
        snippet['publishedAt'],
        snippet['channelId'],
        snippet['title'],
        snippet['description'],
        snippet['channelTitle']
    )

    return row


def format_comment(item):
    meta = item['snippet']
    snippet = getpath(item, ['snippet', 'topLevelComment', 'snippet'])

    row = YouTubeComment(
        meta['videoId'],
        item['id'],
        snippet['authorDisplayName'],
        getpath(snippet, ['authorChannelId', 'value']),
        snippet['textOriginal'],
        int(snippet['likeCount']),
        snippet['publishedAt'],
        snippet['updatedAt'],
        int(meta['totalReplyCount']),
        None
    )

    return row


def format_reply(item, video_id=None):
    snippet = item['snippet']

    row = YouTubeComment(
        video_id if video_id is not None else snippet['videoId'],
        item['id'],
        snippet['authorDisplayName'],
        getpath(snippet, ['authorChannelId', 'value']),
        snippet['textOriginal'],
        int(snippet['likeCount']),
        snippet['publishedAt'],
        snippet['updatedAt'],
        None,
        snippet['parentId']
    )

    return row
