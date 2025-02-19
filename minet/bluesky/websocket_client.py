from urllib.parse import urljoin
from websockets.sync.client import connect, ClientConnection

from minet.bluesky.constants import BLUESKY_FIREHOSE_BASE_URL

# TODO: investigate libipld


class BlueskyWebSocketClient:
    def subscribe_repos(self) -> ClientConnection:
        return connect(
            urljoin(BLUESKY_FIREHOSE_BASE_URL, "com.atproto.sync.subscribeRepos")
        )
