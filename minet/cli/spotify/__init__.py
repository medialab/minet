# =============================================================================
# Minet Spotify CLI Action
# =============================================================================
#
# Logic of the `sp` action.
#

from minet.cli.argparse import command, subcommand, ConfigAction
from minet.spotify.constants import SPOTIFY_MARKETS


SPOTIFY_SEARCH_SHOWS_SUBCOMMAND = subcommand(
    "search-shows",
    "minet.cli.spotify.search_shows",
    title="Minet Spotify Shows Command",
    description="""
        Retrieve podcasts with match on given keyword.
    """,
    epilog="""
        Examples:

        . Getting podcasts with match on keyword:
            $ minet spotify search-shows "'politique*'" --market FR --client-id app-client-id --client-secret app-client-secret-id > shows.csv
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
            "type": str,
            "choices": SPOTIFY_MARKETS,
            "required": True,
        },
    ],
)


SPOTIFY_SEARCH_SHOW_EPISODES_SUBCOMMAND = subcommand(
    "search-episodes",
    "minet.cli.spotify.search_episodes",
    title="Minet Spotify Episodes Command",
    description="""
        Retrieve podcast episodes with match on given keyword.
    """,
    epilog="""
        Examples:

        . Getting podcasts with match on keyword:
            $ minet spotify search-episodes "reforme retraites" --market FR --client-id app-client-id --client-secret app-client-secret-id > episodes.csv
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
            "type": str,
            "choices": SPOTIFY_MARKETS,
            "required": True,
        },
    ],
)

SPOTIFY_GET_SHOW_EPISODES_BY_EPISODE_ID_SUBCOMMAND = subcommand(
    "episodes-by-id",
    "minet.cli.spotify.episodes_by_id",
    title="Minet Spotify Episodes Command",
    description="""
        Retrieve podcast episodes by the episode's ID.
    """,
    epilog="""
        Examples:

        . Getting episodes with ID in column id:
            $ minet spotify episodes id_col -i episode_ids.csv --client-id app-client-id --client-secret app-client-secret-id > episodes.csv
    """,
    variadic_input={
        "dummy_column": "id",
        "item_label": "Id of podcast episode",
        "item_label_plural": "Ids of podcast episodes",
    },
    resumer_kwargs=lambda args: ({"value_column": args.column}),
    arguments=[
        {
            "flags": ["--market"],
            "help": "Market in which the content is distributed.",
            "type": str,
            "choices": SPOTIFY_MARKETS,
            "required": True,
        },
    ],
)

SPOTIFY_GET_SHOW_EPISODES_BY_SHOW_ID_SUBCOMMAND = subcommand(
    "episodes-by-show",
    "minet.cli.spotify.episodes_by_show",
    title="Minet Spotify Episodes Command",
    description="""
        Retrieve a podcast's episodes by the podcast's ID.
    """,
    epilog="""
        Examples:

        . Getting episodes with the podcast's ID in column id:
            $ minet spotify episodes id_col -i show_ids.csv --client-id app-client-id --client-secret app-client-secret-id > episodes.csv
    """,
    variadic_input={
        "dummy_column": "id",
        "item_label": "Id of podcast episode",
        "item_label_plural": "Ids of podcast episodes",
    },
    resumer_kwargs=lambda args: ({"value_column": args.column}),
    arguments=[
        {
            "flags": ["--market"],
            "help": "Market in which the content is distributed.",
            "type": str,
            "choices": SPOTIFY_MARKETS,
            "required": True,
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
    common_arguments=[
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
        },
    ],
    subcommands=[
        SPOTIFY_SEARCH_SHOWS_SUBCOMMAND,
        SPOTIFY_SEARCH_SHOW_EPISODES_SUBCOMMAND,
        SPOTIFY_GET_SHOW_EPISODES_BY_EPISODE_ID_SUBCOMMAND,
        SPOTIFY_GET_SHOW_EPISODES_BY_SHOW_ID_SUBCOMMAND,
    ],
)
