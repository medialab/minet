# =============================================================================
# Minet Mediacloud API Client
# =============================================================================
#
# A unified mediacloud API client that can be used to keep an eye on the
# rate limit and the used token etc.
#
from minet.utils import create_pool
from minet.mediacloud.constants import MEDIACLOUD_DEFAULT_TIMEOUT
from minet.mediacloud.utils import make_simple_call
from minet.mediacloud.search import mediacloud_search
from minet.mediacloud.topic import mediacloud_topic_stories
from minet.mediacloud.formatters import (
    format_media,
    format_feed
)


class MediacloudClient(object):
    def __init__(self, token):
        self.token = token
        self.http = create_pool(timeout=MEDIACLOUD_DEFAULT_TIMEOUT)

    def count(self, query, **kwargs):
        return mediacloud_search(
            self.http,
            self.token,
            query,
            count=True,
            **kwargs
        )

    def search(self, query, **kwargs):
        return mediacloud_search(
            self.http,
            self.token,
            query,
            count=False,
            **kwargs
        )

    def topic_stories(self, topic_id, **kwargs):
        return mediacloud_topic_stories(
            self.http,
            self.token,
            topic_id,
            **kwargs
        )

    def media(self, media_id, format=None):
        return make_simple_call(
            self.http,
            self.token,
            '/media/single',
            format_media,
            format=format,
            arg=media_id,
            single=True
        )

    def feeds(self, media_id, format=None):
        return make_simple_call(
            self.http,
            self.token,
            '/feeds/list',
            format_feed,
            format=format,
            query={
                'media_id': media_id,
                'rows': 100
            }
        )
