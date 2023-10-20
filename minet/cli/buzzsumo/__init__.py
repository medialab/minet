# =============================================================================
# Minet BuzzSumo CLI Action
# =============================================================================
#
# Logic of the `bz` action.
#
from argparse import ArgumentTypeError
from datetime import datetime

from minet.cli.argparse import command, ConfigAction

FIVE_YEARS_IN_SEC = 5 * 365.25 * 24 * 60 * 60


class BuzzSumoDateType(object):
    def __call__(self, date):
        try:
            timestamp = int(datetime.strptime(date, "%Y-%m-%d").timestamp())
        except ValueError:
            raise ArgumentTypeError(
                "dates should have the following format : YYYY-MM-DD."
            )

        if (datetime.now().timestamp() - timestamp) > FIVE_YEARS_IN_SEC:
            raise ArgumentTypeError(
                "you cannot query BuzzSumo using dates before 5 years ago."
            )

        return timestamp


BUZZSUMO_LIMIT_SUBCOMMAND = command(
    "limit",
    "minet.cli.buzzsumo.limit",
    title="Minet Buzzsumo Limit Command",
    description="""
        Call BuzzSumo for a given request and return the remaining number
        of calls for this month contained in the request's headers.
    """,
    epilog="""
        Examples:

        . Returning the remaining number of calls for this month:
            $ minet bz limit --token YOUR_TOKEN
    """,
)

DATE_ARGUMENTS = [
    {
        "flag": "--begin-date",
        "help": "The date you wish to fetch articles from. UTC date should have the following format : YYYY-MM-DD",
        "required": True,
        "type": BuzzSumoDateType(),
    },
    {
        "flag": "--end-date",
        "help": "The date you wish to fetch articles to. UTC date should have the following format : YYYY-MM-DD",
        "required": True,
        "type": BuzzSumoDateType(),
    },
]

BUZZSUMO_DOMAIN_COMMAND = command(
    "domain",
    "minet.cli.buzzsumo.domain",
    title="Minet Buzzsumo Domain Command",
    description="""
        Gather social media information about all the articles crawled by BuzzSumo for one or a list of domain names and over a given period.

        The link to the official documentation: https://developers.buzzsumo.com/reference/articles.
    """,
    epilog="""
        Examples:

        . Returning social media information for one domain name:
            $ minet bz domain 'trump-feed.com' --begin-date 2021-01-01 --end-date 2021-06-30 --token YOUR_TOKEN > trump_feed_articles.csv

        . Returning social media information for a list of domain names in a CSV:
            $ minet bz domain domain_name -i domain_names.csv --select domain_name --begin-date 2019-01-01 --end-date 2020-12-31 --token YOUR_TOKEN > domain_name_articles.csv
    """,
    variadic_input={"dummy_column": "domain_name", "item_label": "domain name"},
    arguments=[
        *DATE_ARGUMENTS,
    ],
)


BUZZSUMO_DOMAIN_SUMMARY_COMMAND = command(
    "domain-summary",
    "minet.cli.buzzsumo.domain_summary",
    title="Minet Buzzsumo Domain Summary Command",
    description="""
        Gather information about the quantity of articles crawled by BuzzSumo for certain domain names and a given period.

        Inform the user about the number of calls (corresponding to the number of pages) needed to request BuzzSumo about those domain names.
    """,
    epilog="""
        Examples:

        . Returning the number of articles and pages found in BuzzSumo for one domain name:
            $ minet bz domain-summary 'nytimes.com' --begin-date 2019-01-01 --end-date 2019-03-01 --token YOUR_TOKEN

        . Returning the number of articles and pages found in BuzzSumo for a list of domain names in a CSV:
            $ minet bz domain-summary domain_name -i domain_names.csv --begin-date 2020-01-01 --end-date 2021-06-15 --token YOUR_TOKEN  > domain_name_summary.csv
    """,
    variadic_input={"dummy_column": "domain_name", "item_label": "domain name"},
    arguments=[
        *DATE_ARGUMENTS,
    ],
)


BUZZSUMO_EXACT_URL_COMMAND = command(
    "exact-url",
    "minet.cli.buzzsumo.exact_url",
    title="Minet Buzzsumo Exact URL Command",
    description="""
        Gather metadata about a specific URL crawled by BuzzSumo in a given time period.
    """,
    epilog="""
        Examples:

        . Returning the metadata found in BuzzSumo for a URL:
            $ minet bz exact-url --begin-date 2020-01-01 --end-date 2023-10-06 --token YOUR_TOKEN 'https://www.lemonde.fr/politique/article/2023/10/06/trois-mois-apres-les-emeutes-emmanuel-macron-tarde-a-prendre-la-mesure-de-la-crise-des-banlieues_6192720_823448.html'
    """,
    variadic_input={"dummy_column": "exact_url", "item_label": "exact url"},
    arguments=[
        *DATE_ARGUMENTS,
    ],
)


BUZZSUMO_COMMAND = command(
    "buzzsumo",
    "minet.cli.buzzsumo",
    title="Minet Buzzsumo Command",
    description="""
        Gather data from the BuzzSumo APIs easily and efficiently.
    """,
    aliases=["bz"],
    common_arguments=[
        {
            "flags": ["-t", "--token"],
            "help": "BuzzSumo API token.",
            "action": ConfigAction,
            "rc_key": ["buzzsumo", "token"],
            "required": True,
        }
    ],
    subcommands=[
        BUZZSUMO_LIMIT_SUBCOMMAND,
        BUZZSUMO_DOMAIN_COMMAND,
        BUZZSUMO_DOMAIN_SUMMARY_COMMAND,
        BUZZSUMO_EXACT_URL_COMMAND,
    ],
)
