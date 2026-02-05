from casanova import Writer

from twitwi.bluesky.constants import PARTIAL_POST_FIELDS
from twitwi.bluesky import format_partial_post_as_csv_row

from minet.cli.utils import with_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.bluesky.websocket_client import BlueskyWebSocketClient
from minet.cli.bluesky.utils import with_bluesky_fatal_errors

# Introduction to Bluesky Tap:
# https://docs.bsky.app/blog/introducing-tap
# https://github.com/bluesky-social/indigo/blob/main/cmd/tap/README.md


# cmd to run to get all posts since the beginning of time (using local tap) (in your cloned repository of indigo):
# go run ./cmd/tap run --collection-filters=app.bsky.feed.post --signal-collection=app.bsky.feed.post


@with_bluesky_fatal_errors
@with_loading_bar(
    title="Getting posts from Bluesky Tap",
    unit="posts",
)
def action(cli_args, loading_bar: LoadingBar):
    client = BlueskyWebSocketClient()

    writer = Writer(cli_args.output, fieldnames=PARTIAL_POST_FIELDS)

    for partial_post in client.get_data_from_local_tap():
        post_row = format_partial_post_as_csv_row(partial_post)
        writer.writerow(post_row)
        loading_bar.advance()