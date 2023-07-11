# =============================================================================
# Minet Mediacloud CLI Action
# =============================================================================
#
# Logic of the `mc` action.
#
from minet.cli.argparse import (
    command,
    ConfigAction,
    OutputAction,
    SplitterType,
)

MEDIACLOUD_MEDIAS_SUBCOMMAND = command(
    "medias",
    "minet.cli.mediacloud.medias",
    title="Minet Mediacloud Medias Command",
    description="""
        Retrieve metadata about a list of Mediacloud medias.
    """,
    variadic_input={"dummy_column": "media", "item_label": "Mediacloud media id"},
    arguments=[
        {
            "flag": "--feeds",
            "help": "If given, path of the CSV file listing media RSS feeds.",
            "action": OutputAction,
        }
    ],
)

MEDIACLOUD_SEARCH_SUBCOMMAND = command(
    "search",
    "minet.cli.mediacloud.search",
    title="Minet Mediacloud Search Command",
    description="""
        Search stories on the Mediacloud platform.

        To learn how to compose more relevant queries, check out this guide:
        https://mediacloud.org/support/query-guide
    """,
    arguments=[
        {"name": "query", "help": "Search query."},
        {
            "flags": ["-c", "--collections"],
            "help": "List of collection ids to search, separated by commas.",
            "type": SplitterType(),
        },
        {
            "flags": ["--filter-query"],
            "help": "Solr filter query `fq` to use. Can be used to optimize some parts of the query.",
        },
        {
            "flags": ["-m", "--medias"],
            "help": "List of media ids to search, separated by commas.",
            "type": SplitterType(),
        },
        {
            "flag": "--publish-day",
            "help": 'Only search stories published on provided day (iso format, e.g. "2018-03-24").',
        },
        {
            "flag": "--publish-month",
            "help": 'Only search stories published on provided month (iso format, e.g. "2018-03").',
        },
        {
            "flag": "--publish-year",
            "help": 'Only search stories published on provided year (iso format, e.g. "2018").',
        },
        {
            "flag": "--skip-count",
            "help": "Whether to skip the first API call counting the number of posts for the progress bar.",
            "action": "store_true",
        },
    ],
)

MEDIACLOUD_TOPIC_STORIES_SUBCOMMAND = command(
    "stories",
    "minet.cli.mediacloud.topic.stories",
    title="Minet Mediacloud Topic Stories Command",
    description="Retrieves the list of stories from a mediacloud topic.",
    arguments=[
        {"name": "topic_id", "help": "Id of the topic."},
        {
            "flag": "--media-id",
            "help": "Return only stories belonging to the given media_ids.",
        },
        {
            "flag": "--from-media-id",
            "help": "Return only stories that are linked from stories in the given media_id.",
        },
    ],
)

MEDIACLOUD_TOPIC_SUBCOMMAND = command(
    "topic",
    "minet.cli.mediacloud.topic",
    title="Minet Mediacloud Topic Commands",
    subcommands=[MEDIACLOUD_TOPIC_STORIES_SUBCOMMAND],
)

MEDIACLOUD_COMMAND = command(
    "mediacloud",
    "minet.cli.mediacloud",
    aliases=["mc"],
    title="Minet Mediacloud Command",
    description="""
        Commands related to the MIT Mediacloud API v2.
    """,
    common_arguments=[
        {
            "flags": ["-t", "--token"],
            "help": 'Mediacloud API token (also called "key" sometimes).',
            "rc_key": ["mediacloud", "token"],
            "action": ConfigAction,
            "required": True,
        }
    ],
    subcommands=[
        MEDIACLOUD_MEDIAS_SUBCOMMAND,
        MEDIACLOUD_SEARCH_SUBCOMMAND,
        MEDIACLOUD_TOPIC_SUBCOMMAND,
    ],
)
