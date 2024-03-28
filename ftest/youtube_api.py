from minet.cli.utils import get_rcfile
from minet.cli.console import console
from minet.youtube import YouTubeAPIClient

config = get_rcfile()
assert config is not None

client = YouTubeAPIClient(config["youtube"]["key"])
console.print(
    client.video("https://www.youtube.com/watch?v=uH7e9wumYWg", raw=True),
    highlight=True,
)
