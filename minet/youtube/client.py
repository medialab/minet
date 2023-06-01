# =============================================================================
# Minet YouTube API Client
# =============================================================================
#
# A handy API client used by the CLI actions.
#
import time
from ebbe import as_chunks
from collections import deque
from ural import urls_from_text, add_query_argument
from ebbe import getpath

from minet.web import (
    create_pool_manager,
    create_request_retryer,
    request,
    retrying_method,
)
from minet.loggers import sleepers_logger
from minet.youtube.utils import (
    ensure_video_id,
    ensure_channel_id,
    get_channel_main_playlist_id,
    seconds_to_midnight_pacific_time,
)
from minet.youtube.urls import YouTubeAPIURLFormatter
from minet.youtube.constants import (
    YOUTUBE_API_MAX_VIDEOS_PER_CALL,
    YOUTUBE_API_MAX_CHANNELS_PER_CALL,
    YOUTUBE_API_DEFAULT_SEARCH_ORDER,
    YOUTUBE_API_SEARCH_ORDERS,
)
from minet.youtube.exceptions import (
    YouTubeDisabledCommentsError,
    YouTubeVideoNotFoundError,
    YouTubeInvalidAPIKeyError,
    YouTubeInvalidAPICallError,
    YouTubeInvalidVideoTargetError,
    YouTubeInvalidChannelTargetError,
    YouTubeExclusiveMemberError,
    YouTubeUnknown403Error,
    YouTubeAccessNotConfiguredError,
)
from minet.youtube.formatters import (
    format_video,
    format_video_snippet,
    format_comment,
    format_reply,
    format_playlist_item_snippet,
    format_channel,
)
from minet.youtube.scrapers import scrape_channel_id


def get_channel_id(channel_target):
    should_scrape, channel_id = ensure_channel_id(channel_target)

    # is a youtube url without the channel ID
    if should_scrape:
        channel_id = scrape_channel_id(channel_target)

    # is not a url
    elif channel_id == channel_target:
        username = channel_target
        if not channel_target.startswith("@"):
            username = "@" + channel_target

        channel_id = scrape_channel_id("https://www.youtube.com/" + username)

        # we didn't get any ID by scraping, channel_target could already be an ID
        if not channel_id:
            channel_id = channel_target

    if channel_id is None:
        raise YouTubeInvalidChannelTargetError

    return channel_id


class YouTubeAPIClient(object):
    def __init__(self, key):
        if not isinstance(key, list):
            key = [key]

        self.keys = {k: True for k in key}
        self.current_key = key[0]
        self.pool_manager = create_pool_manager()

        # YouTube's API is known to crash sometimes...
        self.retryer = create_request_retryer(retry_on_statuses=(503,))
        self.url_formatter = YouTubeAPIURLFormatter()

    @retrying_method()
    def request_json(self, url):
        while True:
            final_url = add_query_argument(url, "key", self.current_key)
            response = request(
                final_url, pool_manager=self.pool_manager, known_encoding="utf-8"
            )
            data = response.json()

            if response.status == 403:
                if data is not None:
                    reason = getpath(data, ["error", "errors", 0, "reason"])

                    if reason == "accessNotConfigured":
                        msg = getpath(data, ["error", "message"])
                        url = next(urls_from_text(msg))
                        raise YouTubeAccessNotConfiguredError(msg, url=url)

                    elif reason == "commentsDisabled":
                        raise YouTubeDisabledCommentsError(url)

                    elif reason == "forbidden":
                        raise YouTubeExclusiveMemberError(url)

                    elif reason == "quotaExceeded":
                        # Current key is exhausted, disabling it and switching to another if there is one
                        if not self.rotate_key():
                            # If all keys are exhausted, start waiting until tomorrow and reset keys
                            sleep_time = seconds_to_midnight_pacific_time() + 10

                            sleepers_logger.warn(
                                "YouTube API limits reached for every key. Will now wait until midnight Pacific time!",
                                extra={
                                    "source": "YouTubeAPIClient",
                                    "sleep_time": 1,
                                },
                            )

                            time.sleep(sleep_time)

                            self.reset_keys()

                        continue

                raise YouTubeUnknown403Error

            if response.status == 404:
                raise YouTubeVideoNotFoundError

            if response.status >= 400:
                if data is not None and "API key not valid" in getpath(
                    data, ["error", "message"], ""
                ):
                    raise YouTubeInvalidAPIKeyError

                raise YouTubeInvalidAPICallError(url, response.status, data)

            return data

    def rotate_key(self):
        self.keys[self.current_key] = False

        available_key = next(
            (key for key, available in self.keys.items() if available), None
        )

        if available_key:
            self.current_key = available_key
            return True

        self.current_key = None
        return False

    def reset_keys(self):
        for key in self.keys:
            if self.current_key is None:
                self.current_key = key

            self.keys[key] = True

    def channels(self, channels_target, key=None, raw=False):
        # TODO: we could chunk per not None
        for group in as_chunks(YOUTUBE_API_MAX_CHANNELS_PER_CALL, channels_target):
            group_data = []

            for item in group:
                target = key(item) if key is not None else item
                try:
                    channel_id = get_channel_id(target)
                    group_data.append((channel_id, item))
                except YouTubeInvalidChannelTargetError:
                    group_data.append((None, item))

            ids = [channel_id for channel_id, _ in group_data if channel_id is not None]

            url = self.url_formatter.channels(ids)

            result = self.request_json(url)

            indexed_result = {}

            # NOTE: as per #753, the "items" key is sometimes absent of the
            # API payload, e.g. if all the enquired channels have been
            # terminated for TOS violations.
            for item in result.get("items", []):
                channel_id = item["id"]

                if not raw:
                    item = format_channel(item)

                indexed_result[channel_id] = item

            for channel_id, item in group_data:
                yield item, indexed_result.get(channel_id)

    def videos(self, videos, key=None, raw=False):
        # TODO: we could chunk per not None
        for group in as_chunks(YOUTUBE_API_MAX_VIDEOS_PER_CALL, videos):
            group_data = []

            for item in group:
                target = key(item) if key is not None else item
                video_id = ensure_video_id(target)
                group_data.append((video_id, item))

            ids = [video_id for video_id, _ in group_data if video_id is not None]

            url = self.url_formatter.videos(ids)

            result = self.request_json(url)

            indexed_result = {}

            for item in result["items"]:
                video_id = item["id"]

                if not raw:
                    item = format_video(item)

                indexed_result[video_id] = item

            for video_id, item in group_data:
                yield item, indexed_result.get(video_id)

    def search(self, query, order=YOUTUBE_API_DEFAULT_SEARCH_ORDER, raw=False):
        if order not in YOUTUBE_API_SEARCH_ORDERS:
            raise TypeError('unknown search order "%s"' % order)

        def generator():
            token = None

            while True:
                url = self.url_formatter.search(query, order=order, token=token)

                result = self.request_json(url)

                token = result.get("nextPageToken")

                for item in result["items"]:
                    if not raw:
                        item = format_video_snippet(item)

                    yield item

                if token is None or len(result["items"]) == 0:
                    break

        return generator()

    def comments(self, video_target, raw=False, full_replies=True):
        video_id = ensure_video_id(video_target)

        if video_id is None:
            raise YouTubeInvalidVideoTargetError

        def generator():
            starting_url = self.url_formatter.comments(video_id)

            queue = deque([(False, video_id, starting_url)])

            while len(queue) != 0:
                is_reply, item_id, url = queue.popleft()

                result = self.request_json(url)

                for item in result["items"]:
                    comment_id = item["id"]
                    replies = getpath(item, ["replies", "comments"], [])
                    total_reply_count = getpath(item, ["snippet", "totalReplyCount"], 0)

                    if not raw:
                        item = (
                            format_comment(item)
                            if not is_reply
                            else format_reply(item, video_id=video_id)
                        )

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
                        replies_url = self.url_formatter.replies(comment_id)

                        queue.append((True, comment_id, replies_url))

                # Next page
                token = result.get("nextPageToken")

                if token is not None and len(result["items"]) != 0:
                    forge = (
                        self.url_formatter.replies
                        if is_reply
                        else self.url_formatter.comments
                    )

                    next_url = forge(item_id, token=token)

                    queue.append((is_reply, item_id, next_url))

        return generator()

    def channel_videos(self, channel_target):
        channel_id = get_channel_id(channel_target)

        playlist_id = get_channel_main_playlist_id(channel_id)

        def generator():
            token = None

            while True:
                url = self.url_formatter.playlist_videos(playlist_id, token=token)

                result = self.request_json(url)

                token = result.get("nextPageToken")

                for item in result["items"]:
                    item = format_playlist_item_snippet(item)

                    yield item

                if token is None or len(result["items"]) == 0:
                    break

        return generator()
