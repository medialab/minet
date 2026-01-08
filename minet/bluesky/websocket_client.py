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

    # Doesn't work when we need to do a full backup (because of storage saturation on a free railway account)
    def subscribe_tap_railway(self, url: str, username: str = None, password: str = None) -> ClientConnection:
        if username and password:
            import base64
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            return connect(url, additional_headers={"Authorization": f"Basic {credentials}"})
        return connect(url)