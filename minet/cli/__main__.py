#!/usr/bin/env python
# =============================================================================
# Minet CLI Endpoint
# =============================================================================
#
# CLI enpoint of the Minet library.
#
import csv
import sys
import shutil
from textwrap import dedent
from argparse import ArgumentParser, FileType, RawTextHelpFormatter

from minet.defaults import DEFAULT_THROTTLE
from minet.cli.defaults import DEFAULT_CONTENT_FOLDER
from minet.cli.utils import BooleanAction

from minet.cli.crowdtangle.constants import CROWDTANGLE_SORT_TYPES, CROWDTANGLE_DEFAULT_RATE_LIMIT

SUBPARSERS = {}

terminal_size = shutil.get_terminal_size()
csv.field_size_limit(sys.maxsize)


def custom_formatter(prog):
    return RawTextHelpFormatter(
        prog,
        max_help_position=50,
        width=terminal_size.columns,
    )


def omit(d, key_to_omit):
    nd = {}

    for k, v in d.items():
        if k == key_to_omit:
            continue

        nd[k] = v

    return nd


# Defining the list of CLI commands
# TODO: generate docs from this data
COMMANDS = {

    # Fetch action subparser
    # --------------------------------------------------------------------------
    'fetch': {
        'description': '''
            Minet Fetch Command
            ===================

            Use multiple threads to fetch batches of urls from a CSV file. The
            command outputs a CSV report with additional metadata about the
            HTTP calls and will generally write the retrieved files in a folder
            given by the user.
        ''',
        'epilog': '''
            examples:

            . Fetching a batch of url from existing CSV file:
                `minet fetch url_column file.csv > report.csv`

            . CSV input from stdin:
                `xsv select url_column file.csv | minet fetch url_column > report.csv`

            . Fetching a single url, useful to pipe into `minet scrape`:
                `minet fetch http://google.com | minet scrape ./scrape.json > scraped.csv`
        ''',
        'arguments': [
            {
                'name': 'column',
                'help': 'Column of the CSV file containing urls to fetch.'
            },
            {
                'name': 'file',
                'help': 'CSV file containing the urls to fetch.',
                'type': FileType('r'),
                'default': sys.stdin,
                'nargs': '?'
            },
            {
                'flag': '--contents-in-report',
                'help': 'Whether to include retrieved contents, e.g. html, directly in the report\nand avoid writing them in a separate folder. This requires to standardize\nencoding and won\'t work on binary formats.',
                'action': 'store_true'
            },
            {
                'flags': ['-d', '--output-dir'],
                'help': 'Directory where the fetched files will be written. Defaults to "%s".' % DEFAULT_CONTENT_FOLDER,
                'default': DEFAULT_CONTENT_FOLDER
            },
            {
                'flags': ['-f', '--filename'],
                'help': 'Name of the column used to build retrieved file names. Defaults to an uuid v4 with correct extension.'
            },
            {
                'flag': '--filename-template',
                'help': 'A template for the name of the fetched files.'
            },
            {
                'flags': ['-g', '--grab-cookies'],
                'help': 'Whether to attempt to grab cookies from your computer\'s chrome browser.',
                'action': 'store_true'
            },
            {
                'flags': ['-H', '--header'],
                'help': 'Custom headers used with every requests.',
                'action': 'append',
                'dest': 'headers'
            },
            {
                'flag': '--standardize-encoding',
                'help': 'Whether to systematically convert retrieved text to UTF-8.',
                'action': 'store_true'
            },
            {
                'flags': ['-o', '--output'],
                'help': 'Path to the output report file. By default, the report will be printed to stdout.'
            },
            {
                'flags': ['-s', '--select'],
                'help': 'Columns to include in report (separated by `,`).'
            },
            {
                'flags': ['-t', '--threads'],
                'help': 'Number of threads to use. Defaults to 25.',
                'type': int,
                'default': 25
            },
            {
                'flag': '--throttle',
                'help': 'Time to wait - in seconds - between 2 calls to the same domain. Defaults to %s.' % DEFAULT_THROTTLE,
                'type': float,
                'default': DEFAULT_THROTTLE
            },
            {
                'flag': '--total',
                'help': 'Total number of lines in CSV file. Necessary if you want to display a finite progress indicator.',
                'type': int
            },
            {
                'flag': '--url-template',
                'help': 'A template for the urls to fetch. Handy e.g. if you need to build urls from ids etc.'
            }
        ]
    },

    # Crowdtangle action subparser
    # --------------------------------------------------------------------------
    'ct': {
        'description': '''
            Minet CrowdTangle Command
            =========================

            Gather data from the CrowdTangle APIs easily and efficiently.
        ''',
        'subparsers': {
            'help': 'Action to perform using the CrowdTangle API.',
            'title': 'actions',
            'dest': 'ct_action',
            'common_arguments': [
                {
                    'flag': '--rate-limit',
                    'help': 'Authorized number of hits by minutes. Defaults to %i.' % CROWDTANGLE_DEFAULT_RATE_LIMIT,
                    'type': int,
                    'default': CROWDTANGLE_DEFAULT_RATE_LIMIT
                },
                {
                    'flags': ['-o', '--output'],
                    'help': 'Path to the output file. By default, everything will be printed to stdout.'
                },
                {
                    'flags': ['-t', '--token'],
                    'help': 'CrowdTangle dashboard API token.'
                }
            ],
            'commands': {
                'leaderboard': {
                    'description': '''
                        Minet CrowdTangle Leaderboard Command
                        =====================================

                        Gather information and aggregated stats about pages and groups of
                        the designated dashboard (indicated by a given token).
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching accounts statistics for every account in your dashboard:
                            `minet ct leaderboard --token YOUR_TOKEN > accounts-stats.csv`
                    ''',
                    'arguments': [
                        {
                            'flag': '--no-breakdown',
                            'help': 'Whether to skip statistics breakdown by post type in the CSV output.',
                            'dest': 'breakdown',
                            'action': BooleanAction,
                            'default': True
                        },
                        {
                            'flags': ['-f', '--format'],
                            'help': 'Output format. Defaults to `csv`.',
                            'choices': ['csv', 'jsonl'],
                            'default': 'csv'
                        },
                        {
                            'flags': ['-l', '--limit'],
                            'help': 'Maximum number of posts to retrieve. Will fetch every post by default.',
                            'type': int
                        },
                        {
                            'flag': '--list-id',
                            'help': 'Optional list id from which to retrieve accounts.'
                        }
                    ]
                },
                'lists': {
                    'description': '''
                        Minet CrowdTangle Lists Command
                        ===============================

                        Retrieve the lists from a CrowdTangle dashboard (indicated by a
                        given token).
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching a dashboard's lists:
                            `minet ct lists --token YOUR_TOKEN > lists.csv`
                    '''
                },
                'posts': {
                    'description': '''
                        Minet CrowdTangle Posts Command
                        ===============================

                        Gather post data from the designated dashboard (indicated by
                        a given token).
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching the 500 most latest posts from a dashboard:
                            `minet ct posts --token YOUR_TOKEN --limit 500 > latest-posts.csv`
                    ''',
                    'arguments': [
                        {
                            'flag': '--end-date',
                            'help': 'The latest date at which a post could be posted (UTC!).'
                        },
                        {
                            'flags': ['-f', '--format'],
                            'help': 'Output format. Defaults to `csv`.',
                            'choices': ['csv', 'jsonl'],
                            'default': 'csv'
                        },
                        {
                            'flag': '--language',
                            'help': 'Language of posts to retrieve.'
                        },
                        {
                            'flags': ['-l', '--limit'],
                            'help': 'Maximum number of posts to retrieve. Will fetch every post by default.',
                            'type': int
                        },
                        {
                            'flag': '--list-ids',
                            'help': 'Ids of the lists from which to retrieve posts, separated by commas.'
                        },
                        {
                            'flag': '--sort-by',
                            'help': 'The order in which to retrieve posts. Defaults to `date`.',
                            'choices': CROWDTANGLE_SORT_TYPES,
                            'default': 'date'
                        },
                        {
                            'flag': '--start-date',
                            'help': 'The earliest date at which a post could be posted (UTC!).'
                        },
                        {
                            'flag': '--url-report',
                            'help': 'Path to an optional report file to write about urls found in posts.',
                            'type': FileType('w')
                        }
                    ]
                },
                'search': {
                    'description': '''
                        Minet CrowdTangle Search Command
                        ================================

                        Search posts on the whole CrowdTangle platform.
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching a dashboard's lists:
                            `minet ct search --token YOUR_TOKEN > posts.csv`
                    ''',
                    'arguments': [
                        {
                            'name': 'terms',
                            'help': 'The search query term or terms.'
                        },
                        {
                            'flag': '--end-date',
                            'help': 'The latest date at which a post could be posted (UTC!).'
                        },
                        {
                            'flags': ['-f', '--format'],
                            'help': 'Output format. Defaults to `csv`.',
                            'choices': ['csv', 'jsonl'],
                            'default': 'csv'
                        },
                        {
                            'flags': ['-l', '--limit'],
                            'help': 'Maximum number of posts to retrieve. Will fetch every post by default.',
                            'type': int
                        },
                        {
                            'flag': '--offset',
                            'help': 'Count offset.',
                            'type': int
                        },
                        {
                            'flag': '--partition-strategy',
                            'help': 'Query partition strategy to use to overcome the API search result limits.',
                            'choices': ['day']
                        },
                        {
                            'flags': ['-p', '--platforms'],
                            'help': 'The platforms, separated by comma from which to retrieve posts.'
                        },
                        {
                            'flag': '--sort-by',
                            'help': 'The order in which to retrieve posts. Defaults to `date`.',
                            'choices': CROWDTANGLE_SORT_TYPES,
                            'default': 'date'
                        },
                        {
                            'flag': '--start-date',
                            'help': 'The earliest date at which a post could be posted (UTC!).'
                        },
                        {
                            'flag': '--types',
                            'help': 'Types of post to include, separated by comma.'
                        },
                        {
                            'flag': '--url-report',
                            'help': 'Path to an optional report file to write about urls found in posts.',
                            'type': FileType('w')
                        }
                    ]
                }
            }
        }
    },

    # Extract action subparser
    # -------------------------------------------------------------------------
    'extract': {
        'description': '''
            Minet Extract Command
            =====================

            Use multiple processes to extract raw text from a batch of HTML files.
            This command can either work on a `minet fetch` report or on a bunch
            of files. It will output an augmented report with the extracted text.
        ''',
        'epilog': '''
            examples:

            . Extracting raw text from a `minet fetch` report:
                `minet extract report.csv > extracted.csv`

            . Working on a report from stdin:
                `minet fetch url_column file.csv | minet extract > extracted.csv`

            . Extracting raw text from a bunch of files:
                `minet extract --glob "./content/*.html" > extracted.csv`
        ''',
        'arguments': [
            {
                'name': 'report',
                'help': 'Input CSV fetch action report file.',
                'type': FileType('r'),
                'default': sys.stdin,
                'nargs': '?'
            },
            {
                'flags': ['-e', '--extractor'],
                'help': 'Extraction engine to use. Defaults to `dragnet`.',
                'choices': ['dragnet', 'html2text']
            },
            {
                'flags': ['-i', '--input-directory'],
                'help': 'Directory where the HTML files are stored. Defaults to "%s".' % DEFAULT_CONTENT_FOLDER,
                'default': DEFAULT_CONTENT_FOLDER
            },
            {
                'flags': ['-o', '--output'],
                'help': 'Path to the output report file. By default, the report will be printed to stdout.'
            },
            {
                'flags': ['-p', '--processes'],
                'help': 'Number of processes to use. Defaults to 4.',
                'type': int,
                'default': 4
            },
            {
                'flags': ['-s', '--select'],
                'help': 'Columns to include in report (separated by `,`).'
            },
            {
                'flag': '--total',
                'help': 'Total number of HTML documents. Necessary if you want to display a finite progress indicator.',
                'type': int
            }
        ]
    },

    # Facebook actions subparser
    # -------------------------------------------------------------------------
    'fb': {
        'description': '''
            Minet Facebook Command
            ======================

            Collects data from Facebook.
        ''',
        'subparsers': {
            'help': 'Action to perform to collect data on Facebook',
            'title': 'actions',
            'dest': 'fb_actions',
            'commands': {
                'comments': {
                    'description': '''
                        Minet Facebook Comments Command
                        ===============================

                        Scrape series of comments on Facebook.
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching a dashboard's lists:
                            `minet fb comments`
                    ''',
                    'arguments': [
                        {
                            'name': 'url',
                            'help': 'Url of the post from which to scrape comments.'
                        },
                        {
                            'flags': ['-c', '--cookie'],
                            'help': 'Authenticated cookie to use or browser from which to extract it (support "firefox" and "chrome").',
                            'default': 'firefox'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'help': 'Path to the output report file. By default, the report will be printed to stdout.'
                        }
                    ]
                }
            }
        }
    },

    # Scrape action subparser
    # -------------------------------------------------------------------------
    'scrape': {
        'description': '''
            Minet Scrape Command
            ====================

            Use multiple processes to scrape data from a batch of HTML files.
            This command can either work on a `minet fetch` report or on a bunch
            of files. It will output the scraped items.
        ''',
        'epilog': '''
            examples:

            . Scraping item from a `minet fetch` report:
                `minet scrape scraper.json report.csv > scraped.csv`

            . Working on a report from stdin:
                `minet fetch url_column file.csv | minet fetch scraper.json > scraped.csv`

            . Scraping items from a bunch of files:
                `minet scrape scraper.json --glob "./content/*.html" > scraped.csv`
        ''',
        'arguments': [
            {
                'name': 'scraper',
                'help': 'Path to a scraper definition file.',
                'type': FileType('r')
            },
            {
                'name': 'report',
                'help': 'Input CSV fetch action report file.',
                'type': FileType('r'),
                'default': sys.stdin,
                'nargs': '?'
            },
            {
                'flags': ['-i', '--input-directory'],
                'help': 'Directory where the HTML files are stored. Defaults to "%s".' % DEFAULT_CONTENT_FOLDER,
                'default': DEFAULT_CONTENT_FOLDER
            },
            {
                'flags': ['-o', '--output'],
                'help': 'Path to the output report file. By default, the report will be printed to stdout.'
            },
            {
                'flags': ['-p', '--processes'],
                'help': 'Number of processes to use. Defaults to 4.',
                'type': int,
                'default': 4
            },
            {
                'flag': '--total',
                'help': 'Total number of HTML documents. Necessary if you want to display a finite progress indicator.',
                'type': int
            }
        ]
    }
}


def add_arguments(subparser, arguments):
    for argument in arguments:
        if 'name' in argument:
            subparser.add_argument(argument['name'], **omit(argument, 'name'))
        elif 'flag' in argument:
            subparser.add_argument(argument['flag'], **omit(argument, 'flag'))
        else:
            subparser.add_argument(*argument['flags'], **omit(argument, 'flags'))


def main():

    # Building the argument parser
    parser = ArgumentParser(prog='minet')
    subparsers = parser.add_subparsers(
        help='Action to execute',
        title='actions',
        dest='action'
    )

    for name, command in COMMANDS.items():
        subparser = subparsers.add_parser(
            name,
            description=dedent(command['description']),
            epilog=dedent(command.get('epilog', '')),
            formatter_class=custom_formatter
        )

        if 'arguments' in command:
            add_arguments(subparser, command['arguments'])

        # TODO: this could be abstracted in recursive construct
        if 'subparsers' in command:
            subparser_subparsers = subparser.add_subparsers(
                help=command['subparsers']['help'],
                title=command['subparsers']['title'],
                dest=command['subparsers']['dest']
            )

            common_arguments = command['subparsers'].get('common_arguments')

            if common_arguments:
                add_arguments(subparser, common_arguments)

            for subname, subcommand in command['subparsers']['commands'].items():
                subsubparser = subparser_subparsers.add_parser(
                    subname,
                    description=dedent(subcommand['description']),
                    epilog=dedent(subcommand.get('epilog', '')),
                    formatter_class=custom_formatter
                )

                if common_arguments:
                    add_arguments(subsubparser, common_arguments)

                if 'arguments' in subcommand:
                    add_arguments(subsubparser, subcommand['arguments'])

        SUBPARSERS[name] = subparser

    # Help subparser
    help_suparser = subparsers.add_parser('help')
    help_suparser.add_argument('subcommand', help='Name of the subcommand', nargs='?')
    SUBPARSERS['help'] = help_suparser

    # Parsing arguments and triggering commands
    args = parser.parse_args()

    if args.action == 'ct':
        from minet.cli.crowdtangle import crowdtangle_action
        crowdtangle_action(args)

    elif args.action == 'extract':
        try:
            import dragnet
        except:
            print('The `dragnet` library is not installed. The `extract` command won\'t work.')
            print('To install it correctly, run the following commands in order:')
            print()
            print('  pip install lxml numpy Cython')
            print('  pip install dragnet')
            sys.exit(1)

        from minet.cli.extract import extract_action
        extract_action(args)

    elif args.action == 'fb':
        from minet.cli.facebook import facebook_action
        facebook_action(args)

    elif args.action == 'fetch':
        from minet.cli.fetch import fetch_action
        fetch_action(args)

    elif args.action == 'help':
        # TODO: handle sub commands?
        target_subparser = SUBPARSERS.get(args.subcommand)

        if target_subparser is None:
            parser.print_help()
        else:
            target_subparser.print_help()

    elif args.action == 'scrape':
        from minet.cli.scrape import scrape_action
        scrape_action(args)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
