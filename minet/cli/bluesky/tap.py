import json

from minet.cli.utils import with_loading_bar
from minet.cli.loading_bar import LoadingBar
from minet.bluesky.websocket_client import BlueskyWebSocketClient
from minet.cli.bluesky.utils import with_bluesky_fatal_errors
# from minet.cli.console import console


# Introduction to Bluesky Tap:
# https://docs.bsky.app/blog/introducing-tap
# https://github.com/bluesky-social/indigo/blob/main/cmd/tap/README.md

# cmd to run to get all posts since the beginning of time (using local tap) (in your cloned repository of indigo):
# go run ./cmd/tap run --disable-acks=true --full-network=true --collection-filters="app.bsky.feed.post"


@with_bluesky_fatal_errors
@with_loading_bar(
    title="Getting posts from Bluesky Tap",
    unit="posts",
)
def action(cli_args, loading_bar: LoadingBar):
    client = BlueskyWebSocketClient()

    # with client.subscribe_tap_railway("wss://tap-medialab.up.railway.app/channel", username="admin", password="3addc000907032d324340fd15209d603") as socket:
    with client.subscribe_local_tap() as socket:
        while True:
            payload = socket.recv()
            data = json.loads(payload)
            # console.print(data, highlight=True)
            loading_bar.inc_stat(data.get("record", {}).get("record", {}).get("$type", "").split(".")[-1], style="info")
            # # console.print(data.get("record", {}).get("record", {}).get("createdAt"), highlight=True)
            # break
            loading_bar.advance()
