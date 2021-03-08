# =============================================================================
# Minet YouTube API Client
# =============================================================================
#
# A handy API client used by the CLI actions.
#
from ebbe import as_chunks

from minet.utils import create_pool, request_json, nested_get
from minet.youtube.utils import ensure_video_id
from minet.youtube.constants import (
    YOUTUBE_API_BASE_URL,
    YOUTUBE_API_MAX_VIDEOS_PER_CALL
)
from minet.youtube.exceptions import (
    YouTubeInvalidAPIKeyError,
    YouTubeInvalidAPICall
)


def forge_videos_url(key, ids):
    data = {
        'base': YOUTUBE_API_BASE_URL,
        'ids': ','.join(ids),
        'key': key
    }

    return '%(base)s/videos?id=%(ids)s&key=%(key)s&part=snippet,statistics,contentDetails' % data


class YouTubeAPIClient(object):
    def __init__(self, key, before_sleep=None):
        self.key = key
        self.http = create_pool()
        self.before_sleep = before_sleep

    def request_json(self, url):
        err, response, data = request_json(self.http, url)

        if err:
            raise err

        if response.status == 403:
            print(data)

        if response.status >= 400:
            if data is not None and 'API key not valid' in nested_get(['error', 'message'], data, ''):
                raise YouTubeInvalidAPIKeyError

            raise YouTubeInvalidAPICall(url, response.status, data)

    def videos(self, videos, key=None):
        for group in as_chunks(YOUTUBE_API_MAX_VIDEOS_PER_CALL, videos):
            indexed = {}

            for item in group:
                target = key(item) if key is not None else item
                video_id = ensure_video_id(target)

                if video_id is not None:
                    indexed[video_id] = item

            ids = list(indexed.keys())

            url = forge_videos_url(self.key, ids)

            self.request_json(url)
