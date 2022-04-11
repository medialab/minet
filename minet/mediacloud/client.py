# =============================================================================
# Minet Mediacloud API Client
# =============================================================================
#
# A unified mediacloud API client that can be used to keep an eye on the
# rate limit and the used token etc.
#
from minet.web import create_pool
from minet.mediacloud.constants import MEDIACLOUD_DEFAULT_TIMEOUT
from minet.mediacloud.utils import make_simple_call
from minet.mediacloud.search import mediacloud_search
from minet.mediacloud.topic import mediacloud_topic_stories
from minet.mediacloud.formatters import format_media, format_feed


class MediacloudAPIClient(object):
    def __init__(self, token):
        self.token = token
        self.pool = create_pool(timeout=MEDIACLOUD_DEFAULT_TIMEOUT)

    def count(self, query, **kwargs):
        return mediacloud_search(self.pool, self.token, query, count=True, **kwargs)

    def search(self, query, **kwargs):
        return mediacloud_search(self.pool, self.token, query, count=False, **kwargs)

    def topic_stories(self, topic_id, **kwargs):
        return mediacloud_topic_stories(self.pool, self.token, topic_id, **kwargs)

    def media(self, media_id, **kwargs):
        return make_simple_call(
            self.pool,
            self.token,
            "/media/single",
            format_media,
            arg=media_id,
            single=True,
            **kwargs
        )

    def feeds(self, media_id, **kwargs):
        return make_simple_call(
            self.pool,
            self.token,
            "/feeds/list",
            format_feed,
            query={"media_id": media_id, "rows": 100},
            **kwargs
        )
