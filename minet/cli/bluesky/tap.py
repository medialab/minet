# import json

from minet.cli.utils import with_loading_bar
from minet.cli.loading_bar import LoadingBar
from minet.bluesky.websocket_client import BlueskyWebSocketClient
from minet.cli.bluesky.utils import with_bluesky_fatal_errors
# from minet.cli.console import console




# Introduction to Bluesky Tap:
# https://docs.bsky.app/blog/introducing-tap


@with_bluesky_fatal_errors
@with_loading_bar(
    title="Getting posts from Bluesky Tap",
    unit="posts",
)
def action(cli_args, loading_bar: LoadingBar):
    client = BlueskyWebSocketClient()

    with client.subscribe_local_tap() as socket:
        while True:
            _payload = socket.recv()
            # data = json.loads(payload)
            # console.print(data, highlight=True)
            # # console.print(data.get("record", {}).get("record", {}).get("createdAt"), highlight=True)
            # break
            loading_bar.advance()
