#!/usr/bin/env python
# =============================================================================
# Minet CLI Endpoint
# =============================================================================
#
# CLI enpoint of the Minet library.
#
import sys
import shutil
from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter

from minet.cli.defaults import DEFAULT_CONTENT_FOLDER

SUBPARSERS = {}

terminal_size = shutil.get_terminal_size()

def custom_formatter(prog):
    return ArgumentDefaultsHelpFormatter(
        prog,
        max_help_position=50,
        width=terminal_size.columns,
    )


def main():
    parser = ArgumentParser(prog='minet')
    subparsers = parser.add_subparsers(
        help='action to execute', title='actions', dest='action')

    # Fetch action subparser
    fetch_subparser = subparsers.add_parser(
        'fetch',
        description='Fetches the urls of a given CSV column',
        formatter_class=custom_formatter
    )

    fetch_subparser.add_argument(
        'column',
        help='column of the CSV file containing urls to fetch'
    )

    fetch_subparser.add_argument(
        'file',
        help='CSV file containing the urls to fetch',
        type=FileType('r'),
        default=sys.stdin,
        nargs='?'
    )

    fetch_subparser.add_argument(
        '-d', '--output-dir',
        help='directory where the fetched files will be written',
        default=DEFAULT_CONTENT_FOLDER
    )
    fetch_subparser.add_argument(
        '-f', '--filename',
        help='name of the column used to build retrieved file names. defaults to uuid v4'
    )
    fetch_subparser.add_argument(
        '--standardize-encoding',
        help='whether to systematically convert retrieved text to UTF-8',
        action='store_true'
    )
    fetch_subparser.add_argument(
        '-o', '--output',
        help='path to the report file'
    )
    fetch_subparser.add_argument(
        '-s', '--select',
        help='columns to include in report (separated by `,`)'
    )
    fetch_subparser.add_argument(
        '-t', '--threads',
        help='number of threads to use',
        type=int,
        default=25
    )
    fetch_subparser.add_argument(
        '--total',
        help='total number of lines in CSV file. necessary if you want a finite progress indicator',
        type=int
    )

    # TODO: lru_cache, normalize urls, print current urls? print end report?

    SUBPARSERS['fetch'] = fetch_subparser

    # Extract action subparser
    extract_subparser = subparsers.add_parser(
        'extract',
        description='Uses multiple processes to extract the main content of HTML pages using `dragnet`.',
        formatter_class=custom_formatter
    )

    extract_subparser.add_argument(
        'report',
        help='input CSV fetch action report file',
        type=FileType('r'),
        default=sys.stdin,
        nargs='?'
    )

    extract_subparser.add_argument(
        '-i', '--input-directory',
        help='directory where the HTML files are stored'
    )
    extract_subparser.add_argument(
        '-o', '--output',
        help='path to the output report file'
    )
    extract_subparser.add_argument(
        '-p', '--processes',
        help='number of processes to use',
        type=int,
        default=4
    )
    extract_subparser.add_argument(
        '-s', '--select',
        help='columns to include in report (separated by `,`)'
    )
    extract_subparser.add_argument(
        '--total',
        help='total number of HTML documents. necessary if you want a finite progress indicator',
        type=int
    )

    SUBPARSERS['extract'] = extract_subparser

    help_suparser = subparsers.add_parser('help')
    help_suparser.add_argument('subcommand', help='name of the subcommand')
    SUBPARSERS['help'] = help_suparser

    args = parser.parse_args()

    if args.action == 'help':
        target_subparser = SUBPARSERS.get(args.subcommand)

        if target_subparser is None:
            parser.print_help()
        else:
            target_subparser.print_help()

    elif args.action == 'fetch':
        from minet.cli.fetch import fetch_action
        fetch_action(args)

    elif args.action == 'extract':
        from minet.cli.extract import extract_action
        extract_action(args)

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
