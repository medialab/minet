# =============================================================================
# Minet YouTube API Client
# =============================================================================
#
# A handy API client used by the CLI actions.
#
import time
from ebbe import as_chunks
from collections import deque
from urllib.parse import quote
from ebbe import getpath

from minet.web import create_pool, request_json
from minet.youtube.utils import ensure_video_id, seconds_to_midnight_pacific_time
from minet.youtube.constants import (
    YOUTUBE_API_BASE_URL,
    YOUTUBE_API_MAX_VIDEOS_PER_CALL,
    YOUTUBE_API_MAX_COMMENTS_PER_CALL,
    YOUTUBE_API_DEFAULT_SEARCH_ORDER,
    YOUTUBE_API_SEARCH_ORDERS
)
from minet.youtube.exceptions import (
    YouTubeInvalidAPIKeyError,
    YouTubeInvalidAPICall,
    YouTubeInvalidVideoId
)
from minet.youtube.formatters import (
    format_video,
    format_video_snippet,
    format_comment,
    format_reply
)


def forge_videos_url(key, ids):
    data = {
        'base': YOUTUBE_API_BASE_URL,
        'ids': ','.join(ids),
        'key': key
    }

    return '%(base)s/videos?id=%(ids)s&key=%(key)s&part=snippet,statistics,contentDetails' % data


def forge_search_url(key, query, order, token=None):
    data = {
        'base': YOUTUBE_API_BASE_URL,
        'order': YOUTUBE_API_DEFAULT_SEARCH_ORDER,
        'query': quote(query),
        'key': key,
        'count': YOUTUBE_API_MAX_VIDEOS_PER_CALL
    }

    url = '%(base)s/search?part=snippet&maxResults=%(count)i&q=%(query)s&type=video&order=%(order)s&key=%(key)s' % data

    if token is not None:
        url += '&pageToken=%s' % token

    return url


def forge_comments_url(key, video_id, token=None):
    data = {
        'base': YOUTUBE_API_BASE_URL,
        'key': key,
        'count': YOUTUBE_API_MAX_COMMENTS_PER_CALL,
        'video_id': video_id
    }

    url = '%(base)s/commentThreads?videoId=%(video_id)s&key=%(key)s&part=snippet,replies&maxResults=%(count)s' % data

    if token is not None:
        url += '&pageToken=%s' % token

    return url


def forge_replies_url(key, comment_id, token=None):
    data = {
        'base': YOUTUBE_API_BASE_URL,
        'key': key,
        'comment_id': comment_id,
        'count': YOUTUBE_API_MAX_COMMENTS_PER_CALL
    }

    url = '%(base)s/comments?part=snippet&parentId=%(comment_id)s&key=%(key)s&maxResults=%(count)s' % data

    if token is not None:
        url += '&pageToken=%s' % token

    return url


class YouTubeAPIClient(object):
    def __init__(self, key, before_sleep_until_midnight=None):
        self.key = key
        self.pool = create_pool()
        self.before_sleep = before_sleep_until_midnight

    def request_json(self, url):
        err, response, data = request_json(url, pool=self.pool)

        if err:
            raise err

        if response.status == 403:
            sleep_time = seconds_to_midnight_pacific_time() + 10

            if callable(self.before_sleep):
                self.before_sleep(sleep_time)

            time.sleep(sleep_time)

            return self.request_json(url)

        if response.status >= 400:
            if data is not None and 'API key not valid' in getpath(data, ['error', 'message'], ''):
                raise YouTubeInvalidAPIKeyError

            raise YouTubeInvalidAPICall(url, response.status, data)

        return data

    def videos(self, videos, key=None, raw=False):

        # TODO: we could chunk per not None
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

    def search(self, query, order=YOUTUBE_API_DEFAULT_SEARCH_ORDER, raw=False):
        if order not in YOUTUBE_API_SEARCH_ORDERS:
            raise TypeError('unkown search order "%s"' % order)

        def generator():
            token = None

            while True:
                url = forge_search_url(
                    self.key,
                    query,
                    order=order
                )

                result = self.request_json(url)

                token = result.get('nextPageToken')

                for item in result['items']:
                    if not raw:
                        item = format_video_snippet(item)

                    yield item

                if token is None or len(result['items']) == 0:
                    break

        return generator()

    def comments(self, video_target, raw=False, full_replies=True):
        video_id = ensure_video_id(video_target)

        if video_id is None:
            raise YouTubeInvalidVideoId

        def generator():
            starting_url = forge_comments_url(
                self.key,
                video_id
            )

            queue = deque([(False, video_id, starting_url)])

            while len(queue) != 0:
                is_reply, item_id, url = queue.popleft()

                result = self.request_json(url)

                for item in result['items']:
                    comment_id = item['id']
                    replies = getpath(item, ['replies', 'comments'], [])
                    total_reply_count = getpath(item, ['snippet', 'totalReplyCount'], 0)

                    if not raw:
                        item = format_comment(item) if not is_reply else format_reply(item, video_id=video_id)

                    yield item

                    if is_reply:
                        continue

                    # Getting replies
                    if not full_replies or len(replies) >= total_reply_count:
                        for reply in replies:
                            if not raw:
                                reply = format_reply(reply)

                            yield reply
                    elif total_reply_count > 0:
                        replies_url = forge_replies_url(
                            self.key,
                            comment_id
                        )

                        queue.append((True, comment_id, replies_url))

                if len(result['items']) == 0:
                    break

                # Next page
                token = result.get('nextPageToken')

                if token is not None:
                    forge = forge_replies_url if is_reply else forge_comments_url

                    next_url = forge(
                        self.key,
                        item_id,
                        token=token
                    )

                    queue.append((is_reply, item_id, next_url))

        return generator()
