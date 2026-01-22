import websockets
import json
from queue import Queue
from datetime import timezone, datetime

# import libipld
# import time

from casanova.writer import Writer

from twitwi.bluesky.constants import PARTIAL_POST_FIELDS
from twitwi.bluesky import format_partial_post_as_csv_row, normalize_partial_post

from minet.cli.utils import with_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.cli.console import console

from minet.bluesky.websocket_client import BlueskyWebSocketClient


# JetStream doc
# https://github.com/bluesky-social/jetstream#

# It seems that the cursor param can be used to start from a given timestamp
# (in microseconds since epoch) only up to one day in the past
# uri = "wss://" + bsky_jetstream_public_instances[1] + "/subscribe?wantedCollections=app.bsky.feed.post&cursor=1733111630000000"

@with_bluesky_fatal_errors
@with_loading_bar(
    title="Getting posts from Bluesky Jetstream firehose",
    unit="posts",
)
def action(cli_args, loading_bar: LoadingBar):

    suffix = "?wantedCollections=app.bsky.feed.post"
    if cli_args.since:
        cli_args.since = cli_args.since.replace(tzinfo=timezone.utc)
        since_timestamp = int(cli_args.since.timestamp() * 1_000_000)
        suffix += f"&cursor={since_timestamp}"

    # registering last seen uris to avoid duplicates when reconnecting
    # 50K posts is the number of posts published every 10 minutes on Bluesky
    last_50k_uris = Queue(maxsize=50000)
    most_recent_datetime:str = None

    client = BlueskyWebSocketClient()

    with client.subscribe_repos(True, suffix) as socket:
        loading_bar.set_title("Listening to Bluesky Jetstream firehose...")
        writer = Writer(cli_args.output, fieldnames=PARTIAL_POST_FIELDS)

        while True:
            try:
                original_message = socket.recv()
                message = json.loads(original_message)
                # post_time = datetime.datetime.fromtimestamp(int(message.get("time_us")) / 1000000)
                # datetime_now = datetime.datetime.now()
                # time_diff = datetime_now - post_time
                # if time_diff.total_seconds() < 5:
                #     console.print(f"[red]WARNING[/red]: Received a post with a delay greater than 5 seconds ({time_diff.total_seconds()} seconds). The post time is {post_time} and the current time is {datetime_now}.", style="bold yellow")
                if not message.get("commit"):
                    # Skipping creation/update of accounts messages
                    if message.get("kind").lower().strip() not in ["identity", "account"]:
                        console.print(f"Unknown message kind:\n{original_message}", highlight=True, style="bold red")
                    continue

                if message.get("commit", {}).get("operation", "") not in ["delete", "update"]:
                    if message.get("commit", {}).get("operation", "") == "create":
                        partial_post = normalize_partial_post(message)
                        if partial_post["uri"] in last_50k_uris.queue:
                            continue  # skip duplicates in last 50k

                        row = format_partial_post_as_csv_row(
                            partial_post,
                        )
                        writer.writerow(row)
                        loading_bar.advance()
                        if last_50k_uris.full():
                            last_50k_uris.get()
                        last_50k_uris.put(partial_post["uri"])
                        most_recent_datetime = partial_post["local_time"]
                    else:
                        url = f"https://bsky.app/profile/{message.get('did', 'UNKNOWN')}/post/{message.get('commit', {}).get('rkey', 'UNKNOWN')}"
                        console.print(f"Unknown operation for this post: [blue]{url}[/blue]\n{message}", style="bold red")
            except websockets.ConnectionClosed as e:
                console.print(f"Connection closed: {e}\nreconnecting...", highlight=True)
                suffix = "?wantedCollections=app.bsky.feed.post"
                if most_recent_datetime:
                    since_timestamp = int(datetime.strptime(most_recent_datetime, "%Y-%m-%dT%H:%M:%S.%f").timestamp() * 1_000_000)
                else:
                    since_timestamp = int(datetime.now().timestamp() * 1_000_000)
                # getting back 5 minutes to avoid missing posts
                since_timestamp -= 300 * 1_000_000
                suffix += f"&cursor={since_timestamp}"
                socket = client.subscribe_repos(True, suffix)
                continue

            except KeyboardInterrupt:
                console.print("Keyboard interrupt received. Exiting...")
                break
            except Exception as e:
                continue
                console.print(f"Error: {e}", highlight=True)


