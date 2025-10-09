import sys
import json
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
#     "https://bsky.app/profile/pecqueuxanthony.bsky.social/post/3lkizm6uvhc2b",
#     "https://bsky.app/profile/annemascret.bsky.social/post/3lkksxdlabk2y",
#     "https://bsky.app/profile/pierre.senellart.com/post/3lkhaibfxv22b",
#     "https://bsky.app/profile/servannemarzin.bsky.social/post/3lkgoqgzhg22k",
#     "https://bsky.app/profile/roppick.bsky.social/post/3lk7najt7s22j",
#     "https://bsky.app/profile/tracklist.com.br/post/3lk7xgxguf22k",
#     "https://bsky.app/profile/snesupfsu.bsky.social/post/3lkkbdz7uxs2s",
#     "https://bsky.app/profile/p4bl0.net/post/3lkgnjzh6ec2g",
#     "https://bsky.app/profile/p4bl0.net/post/3lkeafh3kt22v",
#     "https://bsky.app/profile/bricabraque.bsky.social/post/3lkdnb2gtzk2c",
#     "https://bsky.app/profile/alinenaft.bsky.social/post/3kcoegjbnp525",
#     "https://bsky.app/profile/zahiahamdane.bsky.social/post/3lk4jgruhzk2s",
#     "https://bsky.app/profile/boogheta.bsky.social/post/3ljpthyfcqs2e",
#     "https://bsky.app/profile/shiseptiana.bsky.social/post/3lkbalaxeys2v",
#     "https://bsky.app/profile/danabra.mov/post/3ll4whwghy22y",
#     "https://bsky.app/profile/yomguithereal.bsky.social/post/3kbg7jgtddn2w",
#     "https://bsky.app/profile/fredbourget.bsky.social/post/3lpoug3ljdw27"
      "https://bsky.app/profile/NewYork.activitypub.awakari.com.ap.brid.gy/post/3lkctsyce5f42"
]

did_at_uris = [client.resolve_post_url(post_url) for post_url in post_urls]

DATA = []

for post_data in client.get_posts(did_at_uris, return_raw=True):
    console.print(post_data, highlight=True)
    DATA.append(post_data)

#profiles = [
#    "yomguithereal.bsky.social",
#    "boogheta.bsky.social",
#    "medialab-scpo.bsky.social",
#    "nytimes.com",
#]

#for profile in client.get_profiles(profiles):
#    DATA.append(profile)
#    console.print(profile, highlight=True)

with open("dump.json", "w") as f:
    json.dump(DATA, f, ensure_ascii=False, indent=2)

# client.resolve_handle("yomguithereal.bsky.social")

# for post in client.search_posts("test"):
#     console.print(post, highlight=True)

# client = BlueskyWebSocketClient()

# with client.subscribe_repos() as socket:
#     while True:
#         payload = socket.recv()
#         header, body = libipld.decode_dag_cbor_multi(payload)
#         console.print(header, highlight=True)
