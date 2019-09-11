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

from minet.cli.crowdtangle.constants import CROWDTANGLE_SORT_TYPES

SUBPARSERS = {}

terminal_size = shutil.get_terminal_size()
csv.field_size_limit(sys.maxsize)


def custom_formatter(prog):
    return RawTextHelpFormatter(
        prog,
        max_help_position=50,
        width=terminal_size.columns,
    )


def main():
    parser = ArgumentParser(prog='minet')
    subparsers = parser.add_subparsers(
        help='Action to execute', title='actions', dest='action')

    # Fetch action subparser
    # -------------------------------------------------------------------------
    fetch_description = dedent(
        '''
        Minet Fetch Command
        ===================

        Use multiple threads to fetch batches of urls from a CSV file. The
        command outputs a CSV report with additional metadata about the
        HTTP calls and will generally write the retrieved files in a folder
        given by the user.
        '''
    )

    fetch_epilog = dedent(
        '''
        examples:

        . Fetching a batch of url from existing CSV file:
            `minet fetch url_column file.csv > report.csv`

        . CSV input from stdin:
            `xsv select url_column file.csv | minet fetch url_column > report.csv`

        . Fetching a single url, useful to pipe into `minet scrape`:
            `minet fetch http://google.com | minet scrape ./scrape.json > scraped.csv`
        '''
    )

    fetch_subparser = subparsers.add_parser(
        'fetch',
        description=fetch_description,
        epilog=fetch_epilog,
        formatter_class=custom_formatter
    )

    fetch_subparser.add_argument(
        'column',
        help='Column of the CSV file containing urls to fetch.'
    )

    fetch_subparser.add_argument(
        'file',
        help='CSV file containing the urls to fetch.',
        type=FileType('r'),
        default=sys.stdin,
        nargs='?'
    )

    fetch_subparser.add_argument(
        '--contents-in-report',
        help='Whether to include retrieved contents, e.g. html, directly in the report\nand avoid writing them in a separate folder. This requires to standardize\nencoding and won\'t work on binary formats.',
        action='store_true'
    )
    fetch_subparser.add_argument(
        '-d', '--output-dir',
        help='Directory where the fetched files will be written. Defaults to "%s".' % DEFAULT_CONTENT_FOLDER,
        default=DEFAULT_CONTENT_FOLDER
    )
    fetch_subparser.add_argument(
        '-f', '--filename',
        help='Name of the column used to build retrieved file names. Defaults to an uuid v4 with correct extension.'
    )
    fetch_subparser.add_argument(
        '--filename-template',
        help='A template for the name of the fetched files.'
    )
    fetch_subparser.add_argument(
        '-g', '--grab-cookies',
        help='Whether to attempt to grab cookies from your computer\'s chrome browser.',
        action='store_true'
    )
    fetch_subparser.add_argument(
        '-H', '--header',
        help='Custom headers used with every requests.',
        action='append',
        dest='headers'
    )
    fetch_subparser.add_argument(
        '--standardize-encoding',
        help='Whether to systematically convert retrieved text to UTF-8.',
        action='store_true'
    )
    fetch_subparser.add_argument(
        '-o', '--output',
        help='Path to the output report file. By default, the report will be printed to stdout.'
    )
    fetch_subparser.add_argument(
        '-s', '--select',
        help='Columns to include in report (separated by `,`).'
    )
    fetch_subparser.add_argument(
        '-t', '--threads',
        help='Number of threads to use. Defaults to 25.',
        type=int,
        default=25
    )
    fetch_subparser.add_argument(
        '--throttle',
        help='Time to wait - in seconds - between 2 calls to the same domain. Defaults to %s.' % DEFAULT_THROTTLE,
        type=float,
        default=DEFAULT_THROTTLE
    )
    fetch_subparser.add_argument(
        '--total',
        help='Total number of lines in CSV file. Necessary if you want to display a finite progress indicator.',
        type=int
    )
    fetch_subparser.add_argument(
        '--url-template',
        help='A template for the urls to fetch. Handy e.g. if you need to build urls from ids etc.'
    )

    # TODO: lru_cache, normalize urls, print current urls? print end report?

    SUBPARSERS['fetch'] = fetch_subparser

    # Crowdtangle actions subparser
    # -------------------------------------------------------------------------
    crowdtangle_description = dedent(
        '''
        Minet CrowdTangle Command
        =========================

        Gather data from the CrowdTangle APIs easily and efficiently.
        '''
    )

    crowdtangle_subparser = subparsers.add_parser(
        'ct',
        description=crowdtangle_description,
        formatter_class=custom_formatter
    )

    crowdtangle_subparser_subparsers = crowdtangle_subparser.add_subparsers(
        help='Action to perform using the CrowdTangle API.',
        title='actions',
        dest='ct_action'
    )

    def common_ct_arguments(sub):
        sub.add_argument(
            '-o', '--output',
            help='Path to the output file. By default, everything will be printed to stdout.'
        )
        sub.add_argument(
            '-t', '--token',
            help='CrowdTangle dashboard API token.'
        )

    common_ct_arguments(crowdtangle_subparser)

    # Crowdtangle leaderboard `ct leaderboard`
    crowdtangle_leaderboard_subparser = crowdtangle_subparser_subparsers.add_parser(
        'leaderboard',
        description=dedent(
            '''
            Minet CrowdTangle Leaderboard Command
            =====================================

            Gather information and aggregated stats about pages and groups of
            the designated dashboard (indicated by a given token).
            '''
        ),
        epilog=dedent(
            '''
            examples:

            . Fetching accounts statistics for every account in your dashboard:
                `minet ct leaderboard --token YOUR_TOKEN > accounts-stats.csv`
            '''
        ),
        formatter_class=custom_formatter
    )

    common_ct_arguments(crowdtangle_leaderboard_subparser)

    crowdtangle_leaderboard_subparser.add_argument(
        '--no-breakdown',
        help='Whether to skip statistics breakdown by post type in the CSV output.',
        dest='breakdown',
        action=BooleanAction,
        default=True
    )
    crowdtangle_leaderboard_subparser.add_argument(
        '-f', '--format',
        help='Output format. Defaults to `csv`.',
        choices=['csv', 'jsonl'],
        default='csv'
    )
    crowdtangle_leaderboard_subparser.add_argument(
        '-l', '--limit',
        help='Maximum number of posts to retrieve. Will fetch every post by default.',
        type=int
    )
    crowdtangle_leaderboard_subparser.add_argument(
        '--list-id',
        help='Optional list id from which to retrieve accounts.'
    )

    # Crowdtangle lists `ct lists`
    crowdtangle_lists_subparser = crowdtangle_subparser_subparsers.add_parser(
        'lists',
        description=dedent(
            '''
            Minet CrowdTangle Lists Command
            ===============================

            Retrieve the lists from a CrowdTangle dashboard (indicated by a
            given token).
            '''
        ),
        epilog=dedent(
            '''
            examples:

            . Fetching a dashboard's lists:
                `minet ct lists --token YOUR_TOKEN > lists.csv`
            '''
        ),
        formatter_class=custom_formatter
    )

    common_ct_arguments(crowdtangle_lists_subparser)

    # Crowdtangle posts `ct posts`
    crowdtangle_posts_subparser = crowdtangle_subparser_subparsers.add_parser(
        'posts',
        description=dedent(
            '''
            Minet CrowdTangle Posts Command
            ===============================

            Gather post data from the designated dashboard (indicated by
            a given token).
            '''
        ),
        epilog=dedent(
            '''
            examples:

            . Fetching the 500 most latest posts from a dashboard:
                `minet ct posts --token YOUR_TOKEN --limit 500 > latest-posts.csv`
            '''
        ),
        formatter_class=custom_formatter
    )

    common_ct_arguments(crowdtangle_posts_subparser)

    crowdtangle_posts_subparser.add_argument(
        '--end-date',
        help='The latest date at which a post could be posted (UTC!).'
    )
    crowdtangle_posts_subparser.add_argument(
        '-f', '--format',
        help='Output format. Defaults to `csv`.',
        choices=['csv', 'jsonl'],
        default='csv'
    )
    crowdtangle_posts_subparser.add_argument(
        '--language',
        help='Language of posts to retrieve.'
    )
    crowdtangle_posts_subparser.add_argument(
        '-l', '--limit',
        help='Maximum number of posts to retrieve. Will fetch every post by default.',
        type=int
    )
    crowdtangle_posts_subparser.add_argument(
        '--list-ids',
        help='Ids of the lists from which to retrieve posts, separated by commas.'
    )
    crowdtangle_posts_subparser.add_argument(
        '--sort-by',
        help='The order in which to retrieve posts. Defaults to `date`.',
        choices=CROWDTANGLE_SORT_TYPES,
        default='date'
    )
    crowdtangle_posts_subparser.add_argument(
        '--start-date',
        help='The earliest date at which a post could be posted (UTC!).'
    )
    crowdtangle_posts_subparser.add_argument(
        '--url-report',
        help='Path to an optional report file to write about urls found in posts.',
        type=FileType('w')
    )

    # Crowdtangle search `ct search`
    crowdtangle_search_subparser = crowdtangle_subparser_subparsers.add_parser(
        'search',
        description=dedent(
            '''
            Minet CrowdTangle Search Command
            ================================

            Search posts on the whole CrowdTangle platform.
            '''
        ),
        epilog=dedent(
            '''
            examples:

            . Fetching a dashboard's lists:
                `minet ct search --token YOUR_TOKEN > posts.csv`
            '''
        ),
        formatter_class=custom_formatter
    )

    common_ct_arguments(crowdtangle_search_subparser)

    crowdtangle_search_subparser.add_argument(
        'terms',
        help='The search query term or terms.'
    )

    crowdtangle_search_subparser.add_argument(
        '--end-date',
        help='The latest date at which a post could be posted (UTC!).'
    )
    crowdtangle_search_subparser.add_argument(
        '-f', '--format',
        help='Output format. Defaults to `csv`.',
        choices=['csv', 'jsonl'],
        default='csv'
    )
    crowdtangle_search_subparser.add_argument(
        '-l', '--limit',
        help='Maximum number of posts to retrieve. Will fetch every post by default.',
        type=int
    )
    crowdtangle_search_subparser.add_argument(
        '--offset',
        help='Count offset.',
        type=int
    )
    crowdtangle_search_subparser.add_argument(
        '--partition-strategy',
        help='Query partition strategy to use to overcome the API search result limits.',
        choices=['day']
    )
    crowdtangle_search_subparser.add_argument(
        '-p', '--platforms',
        help='The platforms, separated by comma from which to retrieve posts.'
    )
    crowdtangle_search_subparser.add_argument(
        '--sort-by',
        help='The order in which to retrieve posts. Defaults to `date`.',
        choices=CROWDTANGLE_SORT_TYPES,
        default='date'
    )
    crowdtangle_search_subparser.add_argument(
        '--start-date',
        help='The earliest date at which a post could be posted (UTC!).'
    )
    crowdtangle_search_subparser.add_argument(
        '--types',
        help='Types of post to include, separated by comma.'
    )
    crowdtangle_search_subparser.add_argument(
        '--url-report',
        help='Path to an optional report file to write about urls found in posts.',
        type=FileType('w')
    )

    SUBPARSERS['ct'] = crowdtangle_subparser

    # Extract action subparser
    # -------------------------------------------------------------------------
    extract_description = dedent(
        '''
        Minet Extract Command
        =====================

        Use multiple processes to extract raw text from a batch of HTML files.
        This command can either work on a `minet fetch` report or on a bunch
        of files. It will output an augmented report with the extracted text.
        '''
    )

    extract_epilog = dedent(
        '''
        examples:

        . Extracting raw text from a `minet fetch` report:
            `minet extract report.csv > extracted.csv`

        . Working on a report from stdin:
            `minet fetch url_column file.csv | minet extract > extracted.csv`

        . Extracting raw text from a bunch of files:
            `minet extract --glob "./content/*.html" > extracted.csv`
        '''
    )

    extract_subparser = subparsers.add_parser(
        'extract',
        description=extract_description,
        epilog=extract_epilog,
        formatter_class=custom_formatter
    )

    extract_subparser.add_argument(
        'report',
        help='Input CSV fetch action report file.',
        type=FileType('r'),
        default=sys.stdin,
        nargs='?'
    )

    extract_subparser.add_argument(
        '-e', '--extractor',
        help='Extraction engine to use. Defaults to `dragnet`.',
        choices=['dragnet', 'html2text']
    )
    extract_subparser.add_argument(
        '-i', '--input-directory',
        help='Directory where the HTML files are stored. Defaults to "%s".' % DEFAULT_CONTENT_FOLDER,
        default=DEFAULT_CONTENT_FOLDER
    )
    extract_subparser.add_argument(
        '-o', '--output',
        help='Path to the output report file. By default, the report will be printed to stdout.'
    )
    extract_subparser.add_argument(
        '-p', '--processes',
        help='Number of processes to use. Defaults to 4.',
        type=int,
        default=4
    )
    extract_subparser.add_argument(
        '-s', '--select',
        help='Columns to include in report (separated by `,`).'
    )
    extract_subparser.add_argument(
        '--total',
        help='Total number of HTML documents. Necessary if you want to display a finite progress indicator.',
        type=int
    )

    SUBPARSERS['extract'] = extract_subparser

    # Facebook actions subparser
    # -------------------------------------------------------------------------
    facebook_description = dedent(
        '''
        Minet Facebook Command
        ======================

        Collects data from Facebook.
        '''
    )

    facebook_subparser = subparsers.add_parser(
        'fb',
        description=facebook_description,
        formatter_class=custom_formatter
    )

    facebook_subparser_subparsers = facebook_subparser.add_subparsers(
        help='Action to perform to collect data on Facebook',
        title='actions',
        dest='fb_action'
    )

    # Facebook comments scraper `fb comments`
    facebook_comments_subparser = facebook_subparser_subparsers.add_parser(
        'comments',
        description=dedent(
            '''
            Minet Facebook Comments Command
            ===============================

            Scrape series of comments on Facebook.
            '''
        ),
        epilog=dedent(
            '''
            examples:

            . Fetching a dashboard's lists:
                `minet fb comments`
            '''
        ),
        formatter_class=custom_formatter
    )

    facebook_comments_subparser.add_argument(
        'url',
        help='Url of the post from which to scrape comments.'
    )

    facebook_comments_subparser.add_argument(
        '-o', '--output',
        help='Path to the output file. By default, everything will be printed to stdout.'
    )

    SUBPARSERS['fb'] = facebook_subparser

    # Scrape action subparser
    # -------------------------------------------------------------------------
    scrape_description = dedent(
        '''
        Minet Scrape Command
        ====================

        Use multiple processes to scrape data from a batch of HTML files.
        This command can either work on a `minet fetch` report or on a bunch
        of files. It will output the scraped items.
        '''
    )

    scrape_epilog = dedent(
        '''
        examples:

        . Scraping item from a `minet fetch` report:
            `minet scrape scraper.json report.csv > scraped.csv`

        . Working on a report from stdin:
            `minet fetch url_column file.csv | minet fetch scraper.json > scraped.csv`

        . Scraping items from a bunch of files:
            `minet scrape scraper.json --glob "./content/*.html" > scraped.csv`
        '''
    )

    scrape_subparser = subparsers.add_parser(
        'scrape',
        description=scrape_description,
        epilog=scrape_epilog,
        formatter_class=custom_formatter
    )

    scrape_subparser.add_argument(
        'scraper',
        help='Path to a scraper definition file.',
        type=FileType('r')
    )

    scrape_subparser.add_argument(
        'report',
        help='Input CSV fetch action report file.',
        type=FileType('r'),
        default=sys.stdin,
        nargs='?'
    )

    scrape_subparser.add_argument(
        '-i', '--input-directory',
        help='Directory where the HTML files are stored. Defaults to "%s".' % DEFAULT_CONTENT_FOLDER,
        default=DEFAULT_CONTENT_FOLDER
    )
    scrape_subparser.add_argument(
        '-o', '--output',
        help='Path to the output report file. By default, the report will be printed to stdout.'
    )
    scrape_subparser.add_argument(
        '-p', '--processes',
        help='Number of processes to use. Defaults to 4.',
        type=int,
        default=4
    )
    scrape_subparser.add_argument(
        '--total',
        help='Total number of HTML documents. Necessary if you want to display a finite progress indicator.',
        type=int
    )

    SUBPARSERS['scrape'] = scrape_subparser

    # Help subparser
    # -------------------------------------------------------------------------
    help_suparser = subparsers.add_parser('help')
    help_suparser.add_argument('subcommand', help='Name of the subcommand', nargs='?')
    SUBPARSERS['help'] = help_suparser

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
