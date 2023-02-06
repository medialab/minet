# =============================================================================
# Minet CrowdTangle CLI Action
# =============================================================================
#
# Logic of the `ct` action.
#
from casanova import RowCountResumer, LastCellResumer

from minet.cli.argparse import BooleanAction, SplitterType, OutputFileAction

# TODO: lazyloading issue
from minet.crowdtangle.constants import (
    CROWDTANGLE_DEFAULT_RATE_LIMIT,
    CROWDTANGLE_SORT_TYPES,
    CROWDTANGLE_DEFAULT_START_DATE,
    CROWDTANGLE_SEARCH_FIELDS,
    CROWDTANGLE_SUMMARY_SORT_TYPES,
)

from minet.cli.argparse import command, subcommand, ConfigAction
from minet.cli.exceptions import InvalidArgumentsError

# TODO: this should probably be a required instead, see #534
def check_token(cli_args):
    if not cli_args.token:
        raise InvalidArgumentsError(
            [
                "A token is needed to be able to access CrowdTangle's API.",
                "You can provide one using the `--token` argument.",
            ]
        )


def crowdtangle_api_subcommand(*args, **kwargs):
    return subcommand(*args, validate=check_token, **kwargs)


FORMAT_ARGUMENT = {
    "flags": ["-f", "--format"],
    "help": "Output format. Defaults to `csv`.",
    "choices": ["csv", "jsonl"],
    "default": "csv",
}

CROWDTANGLE_LEADERBOARD_SUBCOMMAND = crowdtangle_api_subcommand(
    "leaderboard",
    "minet.cli.crowdtangle.leaderboard",
    title="Minet CrowdTangle Leaderboard Command",
    description="""
        Gather information and aggregated stats about pages and groups of the designated dashboard (indicated by a given token).

        For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Leaderboard.
    """,
    epilog="""
        examples:

        . Fetching accounts statistics for every account in your dashboard:
            $ minet ct leaderboard --token YOUR_TOKEN > accounts-stats.csv
    """,
    arguments=[
        {
            "flag": "--no-breakdown",
            "help": "Whether to skip statistics breakdown by post type in the CSV output.",
            "dest": "breakdown",
            "action": BooleanAction,
            "default": True,
        },
        FORMAT_ARGUMENT,
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of accounts to retrieve. Will fetch every account by default.",
            "type": int,
        },
        {
            "flag": "--list-id",
            "help": "Optional list id from which to retrieve accounts.",
        },
        {
            "flag": "--start-date",
            "help": "The earliest date at which to start aggregating statistics (UTC!). You can pass just a year or a year-month for convenience.",
        },
    ],
)

CROWDTANGLE_LISTS_SUBCOMMAND = crowdtangle_api_subcommand(
    "lists",
    "minet.cli.crowdtangle.lists",
    title="Minet CrowdTangle Lists Command",
    description="""
        Retrieve the lists from a CrowdTangle dashboard (indicated by a given token).

        For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Lists.
    """,
    epilog="""
        examples:

        . Fetching a dashboard's lists:
            $ minet ct lists --token YOUR_TOKEN > lists.csv
    """,
)

CROWDTANGLE_POSTS_BY_ID_SUBCOMMAND = crowdtangle_api_subcommand(
    "posts-by-id",
    "minet.cli.crowdtangle.posts_by_id",
    title="Minet CrowdTangle Post By Id Command",
    description="""
        Retrieve metadata about batches of posts using Crowdtangle's API.

        For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Posts#get-postid.
    """,
    epilog="""
        examples:

        . Retrieving information about a batch of posts:
            $ minet ct posts-by-id post-url posts.csv --token YOUR_TOKEN > metadata.csv

        . Retrieving information about a single post:
            $ minet ct posts-by-id 1784333048289665 --token YOUR_TOKEN
    """,
    variadic_input={
        "dummy_column": "post_url_or_id",
        "file_help": "CSV file containing the inquired URLs or ids.",
        "column_help": "Name of the column containing the posts URL or id in the CSV file.",
    },
    selectable=True,
    resumer=RowCountResumer,
    total=True,
)

CROWDTANGLE_POSTS_SUBCOMMAND = crowdtangle_api_subcommand(
    "posts",
    "minet.cli.crowdtangle.posts",
    title="Minet CrowdTangle Posts Command",
    description="""
        Gather post data from the designated dashboard (indicated by a given token).

        For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Posts.
    """,
    epilog="""
        examples:

        . Fetching the 500 most latest posts from a dashboard (a start date must be precised):
            $ minet ct posts --token YOUR_TOKEN --limit 500 --start-date 2021-01-01 > latest-posts.csv

        . If your collection is interrupted, it can be restarted from the last data collected with the --resume option:
            $ minet ct posts --token YOUR_TOKEN --limit 500 --start-date 2021-01-01 --resume --output latest-posts.csv

        . Fetching all the posts from a specific list of groups or pages:
            $ minet ct posts --token YOUR_TOKEN --start-date 2021-01-01 --list-ids YOUR_LIST_ID > posts_from_one_list.csv

        To know the different list ids associated with your dashboard:
            $ minet ct lists --token YOUR_TOKEN
    """,
    resumer=LastCellResumer,
    resumer_kwargs={"value_column": "datetime"},
    arguments=[
        {
            "flag": "--chunk-size",
            "help": "When sorting by date (default), the number of items to retrieve before shifting the inital query to circumvent the APIs limitations. Defaults to 500.",
            "type": int,
            "default": 500,
        },
        {
            "flag": "--end-date",
            "help": "The latest date at which a post could be posted (UTC!). You can pass just a year or a year-month for convenience.",
        },
        FORMAT_ARGUMENT,
        {
            "flag": "--language",
            "help": "Language of posts to retrieve.",
        },
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of posts to retrieve. Will fetch every post by default.",
            "type": int,
        },
        {
            "flag": "--list-ids",
            "help": "Ids of the lists from which to retrieve posts, separated by commas.",
            "type": SplitterType(),
        },
        {
            "flag": "--sort-by",
            "help": "The order in which to retrieve posts. Defaults to `date`.",
            "choices": CROWDTANGLE_SORT_TYPES,
            "default": "date",
        },
        {
            "flag": "--start-date",
            "help": "The earliest date at which a post could be posted (UTC!). You can pass just a year or a year-month for convenience. Defaults to `2010`.",
            "default": CROWDTANGLE_DEFAULT_START_DATE,
        },
    ],
)

CROWDTANGLE_SEARCH_SUBCOMMAND = crowdtangle_api_subcommand(
    "search",
    "minet.cli.crowdtangle.search",
    title="Minet CrowdTangle Search Command",
    description="""
        Search posts on the whole CrowdTangle platform.

        For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Search.
    """,
    epilog="""
        examples:

        . Fetching all the 2021 posts containing the words 'acetylsalicylic acid':
            $ minet ct search 'acetylsalicylic acid' --start-date 2021-01-01 --token YOUR_TOKEN > posts.csv
    """,
    arguments=[
        {"name": "terms", "help": "The search query term or terms."},
        {
            "flag": "--and",
            "help": "AND clause to add to the query terms.",
        },
        {
            "flag": "--chunk-size",
            "help": "When sorting by date (default), the number of items to retrieve before shifting the inital query to circumvent the APIs limitations. Defaults to 500.",
            "type": int,
            "default": 500,
        },
        {
            "flag": "--end-date",
            "help": "The latest date at which a post could be posted (UTC!). You can pass just a year or a year-month for convenience.",
        },
        FORMAT_ARGUMENT,
        {
            "flag": "--in-list-ids",
            "help": "Ids of the lists in which to search, separated by commas.",
            "type": SplitterType(),
        },
        {
            "flag": "--language",
            "help": 'Language ISO code like "fr" or "zh-CN".',
        },
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of posts to retrieve. Will fetch every post by default.",
            "type": int,
        },
        {
            "flag": "--not-in-title",
            "help": "Whether to search terms in account titles also.",
            "action": "store_true",
        },
        {"flag": "--offset", "help": "Count offset.", "type": int},
        {
            "flags": ["-p", "--platforms"],
            "help": "The platforms from which to retrieve links (facebook, instagram, or reddit). This value can be comma-separated.",
            "type": SplitterType(),
        },
        {
            "flag": "--search-field",
            "help": "In what to search the query. Defaults to `text_fields_and_image_text`.",
            "choices": CROWDTANGLE_SEARCH_FIELDS,
        },
        {
            "flag": "--sort-by",
            "help": "The order in which to retrieve posts. Defaults to `date`.",
            "choices": CROWDTANGLE_SORT_TYPES,
            "default": "date",
        },
        {
            "flag": "--start-date",
            "help": "The earliest date at which a post could be posted (UTC!). You can pass just a year or a year-month for convenience. Defaults to `2010`.",
            "default": CROWDTANGLE_DEFAULT_START_DATE,
        },
        {
            "flag": "--types",
            "help": "Types of post to include, separated by comma.",
            "type": SplitterType(),
        },
    ],
)

CROWDTANGLE_SUMMARY_SUBCOMMAND = crowdtangle_api_subcommand(
    "summary",
    "minet.cli.crowdtangle.summary",
    title="Minet CrowdTangle Link Summary Command",
    description="""
        Retrieve aggregated statistics about link sharing on the Crowdtangle API and by platform.

        For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Links.
    """,
    epilog="""
        examples:

        . Computing a summary of aggregated stats for urls contained in a CSV row:
            $ minet ct summary url urls.csv --token YOUR_TOKEN --start-date 2019-01-01 > summary.csv
    """,
    variadic_input={
        "dummy_column": "url",
        "file_help": "CSV file containing the inquired URLs.",
        "column_help": "Name of the column containing the URL in the CSV file.",
    },
    selectable=True,
    total=True,
    arguments=[
        {
            "flags": ["-p", "--platforms"],
            "help": "The platforms from which to retrieve links (facebook, instagram, or reddit). This value can be comma-separated.",
            "type": SplitterType(),
        },
        {
            "name": "--posts",
            "help": "Path to a file containing the retrieved posts.",
            "action": OutputFileAction,
            "stdout_fallback": False,
        },
        {
            "flag": "--sort-by",
            "help": "How to sort retrieved posts. Defaults to `date`.",
            "choices": CROWDTANGLE_SUMMARY_SORT_TYPES,
            "default": "date",
        },
        {
            "flag": "--start-date",
            "help": "The earliest date at which a post could be posted (UTC!). You can pass just a year or a year-month for convenience. Defaults to `2010`.",
            "default": CROWDTANGLE_DEFAULT_START_DATE,
            "required": True
        },
    ],
)


CROWDTANGLE_COMMAND = command(
    "crowdtangle",
    "minet.cli.crowdtangle",
    "Minet Crowdtangle Command",
    aliases=["ct"],
    description="""
        Gather data from the CrowdTangle APIs easily and efficiently.
    """,
    common_arguments=[
        {
            "flag": "--rate-limit",
            "help": "Authorized number of hits by minutes. Defaults to %i. Rcfile key: crowdtangle.rate_limit"
            % CROWDTANGLE_DEFAULT_RATE_LIMIT,
            "type": int,
            "default": CROWDTANGLE_DEFAULT_RATE_LIMIT,
            "rc_key": ["crowdtangle", "rate_limit"],
            "action": ConfigAction,
        },
        {
            "flags": ["-t", "--token"],
            "help": "CrowdTangle dashboard API token. Rcfile key: crowdtangle.token",
            "action": ConfigAction,
            "rc_key": ["crowdtangle", "token"],
        },
    ],
    subcommands=[
        CROWDTANGLE_LEADERBOARD_SUBCOMMAND,
        CROWDTANGLE_LISTS_SUBCOMMAND,
        CROWDTANGLE_POSTS_BY_ID_SUBCOMMAND,
        CROWDTANGLE_POSTS_SUBCOMMAND,
        CROWDTANGLE_SEARCH_SUBCOMMAND,
        CROWDTANGLE_SUMMARY_SUBCOMMAND,
    ],
)
