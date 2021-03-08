# =============================================================================
# Minet YouTube API Client
# =============================================================================
#
# A handy API client used by the CLI actions.
#
from minet.utils import create_pool


class YouTubeAPIClient(object):
    def __init__(self, key):
        self.key = key
        self.http = create_pool()
