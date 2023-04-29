# =============================================================================
# Minet Spotify CLI Action
# =============================================================================
#
# Logic of the `sp` action.
#

from minet.cli.argparse import command, subcommand, ConfigAction


SPOTIFY_SHOWS_SUBCOMMAND = subcommand(
    "shows",
    "minet.cli.spotify.shows",
    title="Minet Spotify Shows Command",
    description="""
        Retrieve podcasts with match on given keyword.
    """,
    epilog="""
        Examples:

        . Getting podcasts with match on keyword:
            $ minet spotify shows "reforme retraites" > shows.csv
    """,
    variadic_input={
        "dummy_column": "keyword",
        "item_label": "Keyword to match in show name or description",
        "item_label_plural": "Keywords to match in show name or description",
    },
    resumer_kwargs=lambda args: ({"value_column": args.column}),
    arguments=[
        {
            "flags": ["--market"],
            "help": "Market in which the content is distributed.",
            "type": str
        },
    ],
)


SPOTIFY_EPISODES_SUBCOMMAND = subcommand(
    "episodes",
    "minet.cli.spotify.episodes",
    title="Minet Spotify Episodes Command",
    description="""
        Retrieve podcast episodes with match on given keyword.
    """,
    epilog="""
        Examples:

        . Getting podcasts with match on keyword:
            $ minet spotify episodes "reforme retraites" > episodes.csv
    """,
    variadic_input={
        "dummy_column": "keyword",
        "item_label": "Keyword to match in episode name or description",
        "item_label_plural": "Keywords to match in episode name or description",
    },
    resumer_kwargs=lambda args: ({"value_column": args.column}),
    arguments=[
        {
            "flags": ["--market"],
            "help": "Market in which the content is distributed.",
            "type": str
        },
    ],
)


SPOTIFY_COMMAND = command(
    "spotify",
    "minet.cli.spotify",
    aliases=["sp"],
    title="Minet Spotify Command",
    description="""
        Gather data from Spotify.
    """,
    common_arguments= [
        {
            "flag": "--client-id",
            "help": "Spotify API client id.",
            "rc_key": ["spotify", "client_id"],
            "action": ConfigAction,
        },
        {
            "flag": "--client-secret",
            "help": "Spotify API secret client id.",
            "rc_key": ["spotify", "client_secret"],
            "action": ConfigAction,
        }
    ],
    subcommands=[
        SPOTIFY_SHOWS_SUBCOMMAND,
        SPOTIFY_EPISODES_SUBCOMMAND
    ],
)
