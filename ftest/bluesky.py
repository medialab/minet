import sys
import websockets

# import libipld
import time
# from atproto import (
#     Client,
#     models,
#     FirehoseSubscribeLabelsClient,
#     FirehoseSubscribeReposClient,
# )

from minet.cli.console import console
from minet.web import request
from minet.cli.utils import get_rcfile
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

conf = get_rcfile()
assert conf is not None

client = BlueskyHTTPClient(conf["bluesky"]["identifier"], conf["bluesky"]["password"])
# print(client.is_access_jwt_expired())
# time.sleep(1)
# print(client.refresh_session())

post_urls = [
    "https://bsky.app/profile/danabra.mov/post/3ll4whwghy22y",
    "https://bsky.app/profile/pierre.senellart.com/post/3lkhaibfxv22b",
    "https://bsky.app/profile/washingtonpost.com/post/3ll4zftq4os2y",
    "https://bsky.app/profile/yomguithereal.bsky.social/post/3kbg7jgtddn2w",
]

for post_url in post_urls:
    print(client.post_url_to_did_at_uri(post_url))

# client.resolve_handle("yomguithereal.bsky.social")

# for post in client.search_posts("test"):
#     console.print(post, highlight=True)

# client = BlueskyWebSocketClient()

# with client.subscribe_repos() as socket:
#     while True:
#         payload = socket.recv()
#         header, body = libipld.decode_dag_cbor_multi(payload)
#         console.print(header, highlight=True)
