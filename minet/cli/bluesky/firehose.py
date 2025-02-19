import libipld

from minet.cli.console import console

from minet.bluesky.websocket_client import BlueskyWebSocketClient


def action(_):
    client = BlueskyWebSocketClient()

    with client.subscribe_repos() as socket:
        while True:
            payload = socket.recv()
            header, _ = libipld.decode_dag_cbor_multi(payload)  # type: ignore
            console.print(header, highlight=True)
