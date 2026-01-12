import json
from typing import Iterator
from urllib.parse import urljoin
from websockets.sync.client import connect, ClientConnection
from websockets.exceptions import ConnectionClosedError

from twitwi.bluesky import normalize_partial_post

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

    # Using Tap from a local Indigo instance
    # example: go run ./cmd/tap run
    def get_data_from_local_tap(self) -> Iterator[dict]:
        with self.subscribe_local_tap() as ws:
            while True:
                try:
                    payload = ws.recv()
                    data = json.loads(payload)

                    # Sending ack
                    ws.send(json.dumps({"type": "ack", "id": data["id"]}))

                    # We only want posts
                    # go run ./cmd/tap run --collection-filters=app.bsky.feed.post --signal-collection=app.bsky.feed.post

                    # should be: "app.bsky.feed.post"
                    record_type = data.get("record", {}).get("record", {}).get("$type", "").split(".")[-1]
                    if record_type:

                        normalized_post = normalize_partial_post(data, app_source="tap")
                        yield normalized_post

                except ConnectionClosedError:
                    # console.print(f"[red]Connection closed:[/red] {e}")
                    break


    # Doesn't work when we need to do a full backup (because of storage saturation on a free railway account)
    def subscribe_tap_railway(self, url: str, username: str = None, password: str = None) -> ClientConnection:
        if username and password:
            import base64
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            return connect(url, additional_headers={"Authorization": f"Basic {credentials}"})
        return connect(url)