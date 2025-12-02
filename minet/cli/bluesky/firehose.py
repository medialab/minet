
import asyncio
import websockets
import json

# import libipld
# import time

from minet.cli.console import console

# from minet.bluesky.websocket_client import BlueskyWebSocketClient

# List of public Bluesky Jetstream instances (c.f. https://docs.bsky.app/blog/jetstream)
bsky_jetstream_public_instances = [
    "jetstream1.us-east.bsky.network",
    "jetstream2.us-east.bsky.network",
    "jetstream1.eu-west.bsky.network",
    "jetstream2.eu-west.bsky.network",
]

# JetStream doc
# https://github.com/bluesky-social/jetstream#

uri = "wss://" + bsky_jetstream_public_instances[1] + "/subscribe?wantedCollections=app.bsky.feed.post&author=evancheval.bsky.social"

# It seems that the cursor param can be used to start from a given timestamp
# (in microseconds since epoch) only up to one day in the past
# uri = "wss://" + bsky_jetstream_public_instances[1] + "/subscribe?wantedCollections=app.bsky.feed.post&cursor=1733111630000000"


def action(_):
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
        async with websockets.connect(uri) as websocket:
            while True:
                try:
                    message = await websocket.recv()
                    message = json.loads(message)
                    if not message.get("commit"):
                        # Skipping creation of accounts messages
                        if message.get("kind").lower().strip() in ["identity", "account"]:
                            continue
                        console.print(message, highlight=True)
                        continue
                    url = f"https://bsky.app/profile/{message['did']}/post/{message['commit']['rkey']}"
                    console.print(url, highlight=True)
                    console.print(message, highlight=True)
                    print(url)
                except websockets.ConnectionClosed as e:
                    console.print(f"Connection closed: {e}", highlight=True)
                    break
                except Exception as e:
                    console.print(f"Error: {e}", highlight=True)

    asyncio.get_event_loop().run_until_complete(listen_to_websocket())


# returning this (url of the post: https://bsky.app/profile/did:plc:vuomqwhe7674a3ga6ofatcku/post/3m6wn6bjmnk2m):

# {
#     'ops': [
#         {
#             'cid': b'\x01q\x12 X\x8fO\x9e\xd0~M6n\xedS\x85Y\x98\x16\xcf\xfd\x02\x91\xfej\xc0\xa3\xf6\xf1\x9d\xaf4\xfb\xd4\x94\xd5',
#             'path': 'app.bsky.feed.post/3m6wn6bjmnk2m',
#             'action': 'create'
#         }
#     ],
#     'rev': '3m6wn6cfv3h2z',
#     'seq': 15802565285,
#     'repo': 'did:plc:vuomqwhe7674a3ga6ofatcku',
#     'time': '2025-12-01T14:27:47.996Z',
#     'blobs': [],
#     'since': '3m6wmmxb6fc27',
#     'blocks': b':\xa2eroots\x81\xd8*X%\x00\x01q\x12 \xc8\xe4[\xc5}\xb7\x96Jv\xa6mVc6\xa0\xb7\xab\x81\xe4\xc8\x8e\xf8ZG\x85\xf5\xc6d\xf3dt\xdegversion\x01\xd1\x01\x01q\x12
# c\x99\x92\x11\x98L;\x9c\'\xff\x8e\x80\x07\xc3\xf0\xf1\x8f\xbc\xda\xfdI\xfa\xc6\xc8>3\xa7\xe8\xbai\xe8\xf0\xa2ae\x81\xa4akX app.bsky.feed.post/3m6sap3w7bs24ap\x00at\xd8*X%\x00\x01q\x12
# z\xd3\x9c\xd7\xf3Uz\x9e-\xbe\x1eg\xe9\'P\xc8Q\xe2\xbb\x9d\x14e\x1c\x9c\xbc\x06\xda\x11\x8c\xbfw\xd7av\xd8*X%\x00\x01q\x12
# \xbeI\xd2\x96G"e\xa1%\xac^\x12\x86\x02\xaf\xf5\xbbr\x16\xd9\xc8\xa0E\xb4\x00[\xe5\x00Q\xcc\xbd\ral\xd8*X%\x00\x01q\x12
# I\x08\xad\x15U\x85\xa7\xe4~\t\xad\xa2n\xdf\x7f\xd5\xca\xccL\xbb1\xb1\\\xec\xfb\x00\x1a\xc7\xde\x9e\xa8\xd8S\x01q\x12
# z\xd3\x9c\xd7\xf3Uz\x9e-\xbe\x1eg\xe9\'P\xc8Q\xe2\xbb\x9d\x14e\x1c\x9c\xbc\x06\xda\x11\x8c\xbfw\xd7\xa2ae\x80al\xd8*X%\x00\x01q\x12
# \xc9`\n!\xe3X\xca!\x80n\xa1\xc1\xaf\xf12\xcb`\x18\x1e\x14\xaf\x853+\xc4Z\xb8\x16\x9dr*\x1f\x9c\x02\x01q\x12
# \xc9`\n!\xe3X\xca!\x80n\xa1\xc1\xaf\xf12\xcb`\x18\x1e\x14\xaf\x853+\xc4Z\xb8\x16\x9dr*\x1f\xa2ae\x82\xa4akX"app.bsky.graph.block/3m6la46uym72xap\x00at\xd8*X%\x00\x01q\x12
# \xe1\xab\xf7\xe5N\xa9w\x81\xe1\x99\xab\xb7j|\x86\xa1\xd8\x1f\xac{{\x9f\x05\xe8\x00\x1c\x83\x1a+G\xe24av\xd8*X%\x00\x01q\x12
# FW\xf2\x91\xfc<\xc9\xda`\x01-\xb0\x01qw\xb3\x90\xbe\xcdF\x93@h\x99\x01\xb0\xbd&]\x83\x9c\x16\xa4akTfollow/3m5t4pxeh6h2vap\x0fat\xf6av\xd8*X%\x00\x01q\x12
# e\x12"\x19~EI\xef\xb2M8v\xe8X\xfd\x0f(9\n\x01 \x86\x90\xf6\x89\xe3$\xfe\xe36\xa6\xbfal\xd8*X%\x00\x01q\x12
# \xb0\xa4B\xd4\xc2*\xe7\x81\xe0\x17!y\xb27\xba0d\xff\xc5\x92\xf0\xdb\xd3\xe9\xe0.\x1c3\xcaWIx\xcd\x04\x01q\x12
# \xb0\xa4B\xd4\xc2*\xe7\x81\xe0\x17!y\xb27\xba0d\xff\xc5\x92\xf0\xdb\xd3\xe9\xe0.\x1c3\xcaWIx\xa2ae\x85\xa4akX app.bsky.feed.post/3m6vc4qcfts2cap\x00at\xf6av\xd8*X%\x00\x01q\x12
# Q}\nN\xe6\xba\xab`Y\xe40*!V\xaf//\xcf>[\xd9D\xd3\xbf9]\xe0\x17\xf1#R\xeb\xa4akIe554yuc2nap\x17at\xd8*X%\x00\x01q\x12
# sd\xfc\xd1\xe4\xcbw\xe6@S\x8b+O\xd1c\xe3\xb9\xdc\xdf3\xd2\xe1^\x19\xe4\xa2\xf2$\xf5\x90\xcc\xdfav\xd8*X%\x00\x01q\x12
# \x8a$\xd97q\x96\x17\xc1\xbb7tW1D\xc0\xd8\x81\x16\x19y\xd2j\xb2\x071\xb0\xaf\xd3\xc2\x04?z\xa4akIw654otk2map\x17at\xd8*X%\x00\x01q\x12
# \xdf]\xa7\x9f\x96\x9a\x8c\xa0\xf3\t!\x93\xa8Cu\x1c\xd3\x1c\x8f\xed\xac\x17p\x0e\xe0\x83m\xdb\x8eg<9av\xd8*X%\x00\x01q\x12
# \xd6\x8a\x01L\xc3\xf2\xd5\x94\xd0\xbe\xac\x0eG\x85(\xa7\xd4\xcf\xb0\xf2\xb4*BU\x910q\xfb\x1duX\x17\xa4akJwl33qnnk26ap\x16at\xd8*X%\x00\x01q\x12
# n\x8ec\x84Q|\x17&T\x1a\xcd\xbf\x02\xdf\xcd[\xf6p\x16\xc6\xde\x1e\xd8YTOI\xcf\xce_&\xb3av\xd8*X%\x00\x01q\x12
# \x87q\x1e\xc0lC\xbeM\xcf\rSWa\xe1M9\xd1]\x82mRnJK_\xc7*\xa7\xa0A\t\xdc\xa4akTrepost/3m5gznc6ewh2vap\x0eat\xd8*X%\x00\x01q\x12
# h{KGc\xc2\xd3\xf5\x84\xd8\x15\x7f35\xd0\xca:l}\xe7\x13\xc3\xe9=\x02\xb1\xc0\xa9Cm\x89=av\xd8*X%\x00\x01q\x12 \xec\xe0\x98
# O\xe9\xce\x8f\n1\x19H\xbc\xe0\x05\xf4\xa7\xcas\xa9\xf0<\xd28\xad\x9aDt\xf5\xb4\x87\xbcal\xd8*X%\x00\x01q\x12 \xb4.VtL\xf1u\xb7Z\x99G\xe4T\x12j\xb7["\xa5Q\x04\xb9V
# $\xa3\x13\xa0\xef>\x02\xf5\xca\x01\x01q\x12 n\x8ec\x84Q|\x17&T\x1a\xcd\xbf\x02\xdf\xcd[\xf6p\x16\xc6\xde\x1e\xd8YTOI\xcf\xce_&\xb3\xa2ae\x82\xa4akX
# app.bsky.feed.post/3m6wn6bjmnk2map\x00at\xf6av\xd8*X%\x00\x01q\x12
# X\x8fO\x9e\xd0~M6n\xedS\x85Y\x98\x16\xcf\xfd\x02\x91\xfej\xc0\xa3\xf6\xf1\x9d\xaf4\xfb\xd4\x94\xd5\xa4akTrepost/3m4uvtag5sa2wap\x0eat\xf6av\xd8*X%\x00\x01q\x12
# \x96\x1aD\x04\xc6\xa3\x02\x86\x97\x91\xcd\xe6\xd4i\x1d\x11\x0e\xb2\x1b=2\xaam\x8a\\\'\x83\x13)y\x1b\xb5al\xf6\xcd\x05\x01q\x12
# X\x8fO\x9e\xd0~M6n\xedS\x85Y\x98\x16\xcf\xfd\x02\x91\xfej\xc0\xa3\xf6\xf1\x9d\xaf4\xfb\xd4\x94\xd5\xa5dtexty\x01*Aww i\'m glad you enjoy my art and espesially my rambling storytelling
# of my oc. \n\n(I will spout more of this story bout my oc at you now Mwahahah!!!).\n\nI love the way you depict the characters both in art and in writing.\n\nYour posts about Ancano
# and Estormo makes me so happy every time i see
# them.e$typerapp.bsky.feed.postelangs\x81benereply\xa2droot\xa2ccidx;bafyreiedcv3vujunn7c7e63zn2sonasofxl2sof7vptp2cv7ymacco47wqcurixFat://did:plc:6mrhlpj5ui74cif5sm56uigd/app.bsky.feed
# .post/3m6vod3x4522dfparent\xa2ccidx;bafyreianfvtn5n2ji5bo6mcgcwagpouby43x7gabvorvumyhxvugdnq35acurixFat://did:plc:6mrhlpj5ui74cif5sm56uigd/app.bsky.feed.post/3m6wmdfy4uk2bicreatedAtx\x
# 182025-12-01T14:27:46.789Z\xe0\x01\x01q\x12 \xc8\xe4[\xc5}\xb7\x96Jv\xa6mVc6\xa0\xb7\xab\x81\xe4\xc8\x8e\xf8ZG\x85\xf5\xc6d\xf3dt\xde\xa6cdidx
# did:plc:vuomqwhe7674a3ga6ofatckucrevm3m6wn6cfv3h2zcsigX@3\xfa\xd5\x00\x1b\x8b\xea\x1b>AV\xfe\x07nWu\x9d\xb8\x94\x10\xe6\xc2\x0b\x9d(\xa4\x1b\x14\xc3\x9c6t9\xc0\x0fvC\xfe\xf7\xc2\xbfb\x
# 89d>\xb8\xc3\x7f\xd2c3\x0f\x9f\xeePP3G\x8d^\xc3\xed\xc02ddata\xd8*X%\x00\x01q\x12
# c\x99\x92\x11\x98L;\x9c\'\xff\x8e\x80\x07\xc3\xf0\xf1\x8f\xbc\xda\xfdI\xfa\xc6\xc8>3\xa7\xe8\xbai\xe8\xf0dprev\xf6gversion\x03',
#     'commit': b'\x01q\x12 \xc8\xe4[\xc5}\xb7\x96Jv\xa6mVc6\xa0\xb7\xab\x81\xe4\xc8\x8e\xf8ZG\x85\xf5\xc6d\xf3dt\xde',
#     'rebase': False,
#     'tooBig': False
# }