from urllib.parse import urljoin
from websockets.sync.client import connect, ClientConnection

from minet.bluesky.constants import BLUESKY_FIREHOSE_BASE_URL,BLUESKY_FIREHOSE_JETSREAM_URLS

# TODO: investigate libipld


class BlueskyWebSocketClient:
    def subscribe_repos(self, using_jetstream: bool = False, suffix: str = "") -> ClientConnection:
        if using_jetstream:
            return connect("wss://" + BLUESKY_FIREHOSE_JETSREAM_URLS[1] + "/subscribe" + suffix)
        return connect(
            urljoin(BLUESKY_FIREHOSE_BASE_URL, "com.atproto.sync.subscribeRepos")
        )

    def subscribe_local_tap(self) -> ClientConnection:
        return connect("ws://localhost:2480/channel")
