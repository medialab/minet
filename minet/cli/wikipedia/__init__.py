from casanova import RowCountResumer

from minet.cli.argparse import command, subcommand

WIKIPEDIA_PAGEVIEWS_SUBCOMMAND = subcommand(
    "pageviews",
    "minet.cli.wikipedia.pageviews",
    title="Minet Wikipedia Pageviews Command",
    resumer=RowCountResumer,
)

WIKIPEDIA_COMMAND = command(
    "wikipedia",
    "minet.cli.wikipedia",
    title="Minet Wikipedia Command",
    aliases=["wiki"],
    subcommands=[],
)
