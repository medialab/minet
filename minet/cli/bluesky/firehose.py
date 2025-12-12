
import asyncio
import websockets
import json

# import libipld
# import time

from casanova.writer import Writer

from twitwi.bluesky.constants import PARTIAL_POST_FIELDS
from twitwi.bluesky import format_partial_post_as_csv_row, normalize_partial_post

from minet.cli.utils import with_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.cli.console import console

# from minet.bluesky.websocket_client import BlueskyWebSocketClient

# List of public Bluesky Jetstream instances (c.f. https://docs.bsky.app/blog/jetstream)
bsky_jetstream_public_instances = [
    "jetstream1.us-east.bsky.network",
    "jetstream2.us-east.bsky.network",
    "jetstream1.us-west.bsky.network",
    "jetstream2.us-west.bsky.network",
]

# JetStream doc
# https://github.com/bluesky-social/jetstream#

URI = "wss://" + bsky_jetstream_public_instances[0] + "/subscribe?wantedCollections=app.bsky.feed.post"

# It seems that the cursor param can be used to start from a given timestamp
# (in microseconds since epoch) only up to one day in the past
# uri = "wss://" + bsky_jetstream_public_instances[1] + "/subscribe?wantedCollections=app.bsky.feed.post&cursor=1733111630000000"

@with_bluesky_fatal_errors
@with_loading_bar(
    title="Getting posts from Bluesky Jetstream firehose",
    unit="posts",
)
def action(cli_args, loading_bar: LoadingBar):
    # client = BlueskyWebSocketClient()

    # with client.subscribe_repos() as socket:
    #     start = time.time()
    #     countingposts = 0
    #     while True:
    #         payload = socket.recv()
    #         header, body = libipld.decode_dag_cbor_multi(payload)  # type: ignore
    #         # console.print(header, highlight=True)
    #         body = dict(body)
    #         blocks = body.get("blocks", None)
    #         if blocks:
    #             console.print(libipld.decode_car(blocks), highlight=True)
    #         if not body.get("repo"):
    #             continue
    #         did = body["repo"]
    #         if not body.get("ops"):
    #             continue
    #         path = body["ops"][0]["path"].split("/")
    #         if path[0] == "app.bsky.feed.post":
    #             post_id = path[-1]
    #             countingposts += 1
    #             if countingposts % 1000 == 0:
    #                 elapsed = time.time() - start
    #                 console.print(
    #                     f"Collected {countingposts} posts in {elapsed:.2f} seconds ({countingposts/elapsed:.2f} posts/sec)",
    #                     highlight=True,
    #                 )
    #             # console.print(f"Post found: https://bsky.app/profile/{did}/post/{post_id}", highlight=True)
    #         elif any(p in path[0] for p in
    #                  ["feed.like", "feed.repost", "graph.follow", "feed.threadgate", "feed.postgate", "graph.list", "graph.listblock" ,"graph.block", "graph.starterpack", "graph.listitem", "actor.status", "actor.profile", "actor.declaration", "notification.declaration", "feed.generator"]):
    #             continue
    #         elif "bsky" in path[0]:
    #             console.print(path[0], highlight=True)

    async def listen_to_websocket():
        uri = URI
        if cli_args.since:
            since_timestamp = int(cli_args.since.timestamp() * 1_000_000)
            uri_with_cursor = uri + f"&cursor={since_timestamp}"
            uri = uri_with_cursor
        async with websockets.connect(uri) as websocket:
                loading_bar.set_title("Listening to Bluesky Jetstream firehose...")
                writer = Writer(cli_args.output, fieldnames=PARTIAL_POST_FIELDS)

                while True:
                    try:
                        original_message = await websocket.recv()
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
                                row = format_partial_post_as_csv_row(
                                    partial_post,
                                )
                                writer.writerow(row)
                                loading_bar.advance()
                                pass
                            else:
                                url = f"https://bsky.app/profile/{message.get('did', 'UNKNOWN')}/post/{message.get('commit', {}).get('rkey', 'UNKNOWN')}"
                                console.print(f"Unknown operation for this post: [blue]{url}[/blue]\n{message}", style="bold red")
                    except websockets.ConnectionClosed as e:
                        console.print(f"Connection closed: {e}", highlight=True)
                        break
                    except KeyboardInterrupt:
                        console.print("Keyboard interrupt received. Exiting...", highlight=True)
                        break
                    except Exception as e:
                        continue
                        console.print(f"Error: {e}", highlight=True)

    asyncio.get_event_loop().run_until_complete(listen_to_websocket())

