import sys
import websockets
import libipld
from atproto import (
    Client,
    models,
    FirehoseSubscribeLabelsClient,
    FirehoseSubscribeReposClient,
)

from minet.cli.console import console
from minet.web import request
from minet.bluesky import BlueskyHTTPClient, BlueskyWebSocketClient

# response = request("https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?q=test")

# for name, value in response.headers.items():
#     print(name, value)
# console.print(response.json(), highlight=True)

# client = Client()
# print(vars(client))
# client.login(sys.argv[1], sys.argv[2])

# response = client.app.bsky.feed.search_posts({"q": "test", "cursor": "25"})
# console.print(models.get_model_as_json(response), highlight=True)

# client = BlueskyHTTPClient(sys.argv[1], sys.argv[2])

# for post in client.search_posts("test"):
#     console.print(post, highlight=True)

client = BlueskyWebSocketClient()

with client.subscribe_repos() as socket:
    payload = socket.recv()

    for message in libipld.decode_dag_cbor_multi(payload):
        print(message)
