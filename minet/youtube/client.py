# =============================================================================
# Minet YouTube API Client
# =============================================================================
#
# A handy API client used by the CLI actions.
#
import time
from ebbe import as_chunks

from minet.utils import create_pool, request_json, nested_get
from minet.youtube.utils import ensure_video_id, seconds_to_midnight_pacific_time
from minet.youtube.constants import (
    YOUTUBE_API_BASE_URL,
    YOUTUBE_API_MAX_VIDEOS_PER_CALL
)
from minet.youtube.exceptions import (
    YouTubeInvalidAPIKeyError,
    YouTubeInvalidAPICall
)
from minet.youtube.formatters import (
    format_video
)


def forge_videos_url(key, ids):
    data = {
        'base': YOUTUBE_API_BASE_URL,
        'ids': ','.join(ids),
        'key': key
    }

    return '%(base)s/videos?id=%(ids)s&key=%(key)s&part=snippet,statistics,contentDetails' % data


class YouTubeAPIClient(object):
    def __init__(self, key, before_sleep_until_midnight=None):
        self.key = key
        self.http = create_pool()
        self.before_sleep = before_sleep_until_midnight

    def request_json(self, url):
        err, response, data = request_json(self.http, url)

        if err:
            raise err

        if response.status == 403:
            sleep_time = seconds_to_midnight_pacific_time() + 10

            if callable(self.before_sleep):
                self.before_sleep(sleep_time)

            time.sleep(sleep_time)

            return self.request_json(url)

        if response.status >= 400:
            if data is not None and 'API key not valid' in nested_get(['error', 'message'], data, ''):
                raise YouTubeInvalidAPIKeyError

            raise YouTubeInvalidAPICall(url, response.status, data)

        return data

    def videos(self, videos, key=None, raw=False):
        for group in as_chunks(YOUTUBE_API_MAX_VIDEOS_PER_CALL, videos):
            group_data = []

            for item in group:
                target = key(item) if key is not None else item
                video_id = ensure_video_id(target)
                group_data.append((video_id, item))

            ids = [video_id for video_id, _ in group_data if video_id is not None]

            url = forge_videos_url(self.key, ids)

            result = self.request_json(url)

            indexed_result = {}

            for item in result['items']:
                video_id = item['id']

                if not raw:
                    item = format_video(item)

                indexed_result[video_id] = item

            for video_id, item in group_data:
                yield item, indexed_result.get(video_id)
