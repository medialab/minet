#!/usr/bin/env python
# =============================================================================
# Minet CLI Endpoint
# =============================================================================
#
# CLI Interface of the Minet library.
#
from os.path import join
import sys
from argparse import ArgumentParser, FileType

from minet.cli.fetch_action import fetch_action

SUBPARSERS = {}


def main():
    parser = ArgumentParser(prog='minet')
    subparsers = parser.add_subparsers(
        help='action to execute', title='actions', dest='action')

    fetch_subparser = subparsers.add_parser(
        'fetch', description='Fetches the HTML of the urls of a given CSV column.')
    fetch_subparser.add_argument('column', help='column')
    fetch_subparser.add_argument(
        'file', help='csv file containing the urls to fetch', type=FileType('r'), default=sys.stdin, nargs='?')
    fetch_subparser.add_argument(
        '--monitoring-file', help='csv file containing the urls to fetch', type=FileType('a+'), default=join('data', 'monitoring.csv'), nargs='?')
    fetch_subparser.add_argument(
        '-s', '--storage-location', help='HTML storage location', default='data')
    fetch_subparser.add_argument(
        '-id', '--id-column', help='url id column', default=None)
    SUBPARSERS['fetch'] = fetch_subparser

    # extract_content_subparser = subparsers.add_parser('extract_content', description='Return the text content of the urls of a given csv')

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

    if args.action == 'fetch':
        fetch_action(args)


if __name__ == '__main__':
    main()
