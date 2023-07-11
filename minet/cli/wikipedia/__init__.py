from casanova import RowCountResumer

from minet.cli.exceptions import InvalidArgumentsError
from minet.cli.argparse import command


def resolve_pageviews_args(cli_args):
    if cli_args.lang is None and cli_args.lang_column is None:
        raise InvalidArgumentsError(
            "This command requires --lang or --lang-column to be given."
        )

    if cli_args.resume and not cli_args.sum:
        raise InvalidArgumentsError("Can only --resume with --sum.")


WIKIPEDIA_PAGEVIEWS_SUBCOMMAND = command(
    "pageviews",
    "minet.cli.wikipedia.pageviews",
    title="Minet Wikipedia Pageviews Command",
    description="""
        Command using the Wikimedia REST API to collect
        pageviews for a given amount of Wikipedia pages.

        See API documentation here for more details:
        https://wikitech.wikimedia.org/wiki/Analytics/AQS/Pageviews
    """,
    variadic_input={"dummy_column": "page"},
    resumer=RowCountResumer,
    resumer_epilog="Will only work with --sum.",
    arguments=[
        {
            "flag": "--start-date",
            "help": "Starting date. Must be of format YYYYMMDD (e.g. 20151031) or YYYYMMDDHH (e.g. 2015103100)",
            "required": True,
        },
        {
            "flag": "--end-date",
            "help": "End date. Must be of format YYYYMMDD (e.g. 20151031) or YYYYMMDDHH (e.g. 2015103100)",
            "required": True,
        },
        {
            "flag": "--agent",
            "help": "Get pageviews by target agent.",
            "default": "all-agents",
        },
        {
            "flag": "--access",
            "help": "Get pageviews by access.",
            "default": "all-access",
        },
        {
            "flags": ["-t", "--threads"],
            "help": "Number of threads to use.",
            "type": int,
            "default": 10,
        },
        {
            "flag": "--granularity",
            "help": "Pageviews granularity.",
            "default": "monthly",
        },
        {
            "flag": "--sum",
            "help": "Whether to sum the collected pageviews rather than outputting them by timestamp.",
            "action": "store_true",
        },
        {"flag": "--lang", "help": "Lang for the given pages."},
        {"flag": "--lang-column", "help": "Name of a CSV column containing page lang."},
    ],
)

WIKIPEDIA_COMMAND = command(
    "wikipedia",
    "minet.cli.wikipedia",
    title="Minet Wikipedia Command",
    aliases=["wiki"],
    subcommands=[WIKIPEDIA_PAGEVIEWS_SUBCOMMAND],
)
