# =============================================================================
# Minet YouTube Formatters
# =============================================================================
#
# Various data formatters for YouTube data.
#


def format_video(item):
    snippet = item['snippet']
    stats = item['statistics']
    details = item['contentDetails']

    row = [
        item['id'],
        snippet['publishedAt'],
        snippet['channelId'],
        snippet['title'],
        snippet['description'],
        snippet['channelTitle'],
        stats.get('viewCount', None),
        stats.get('likeCount', None),
        stats.get('dislikeCount', None),
        stats.get('favoriteCount', None),
        stats.get('commentCount', None),
        details['duration'],
        details['caption']
    ]

    return row
