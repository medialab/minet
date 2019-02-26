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

from minet.cli.fetch import fetch_action

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
        description='Fetches the HTML of the urls of a given CSV column.',
        formatter_class=custom_formatter
    )

    fetch_subparser.add_argument(
        'column',
        help='column of the csv file containing urls to fetch'
    )

    fetch_subparser.add_argument(
        'file',
        help='csv file containing the urls to fetch',
        type=FileType('r'),
        default=sys.stdin,
        nargs='?'
    )
    fetch_subparser.add_argument(
        '-d', '--output-dir',
        help='directory where the fetched files will be written',
        default='content'
    )
    fetch_subparser.add_argument(
        '-t', '--threads',
        help='number of threads to use',
        type=int,
        default=10
    )

    SUBPARSERS['fetch'] = fetch_subparser

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
        fetch_action(args)

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
