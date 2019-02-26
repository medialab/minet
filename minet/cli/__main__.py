#!/usr/bin/env python
# =============================================================================
# Minet CLI Endpoint
# =============================================================================
#
# CLI enpoint of the Minet library.
#
from os.path import join
import sys
from argparse import ArgumentParser, FileType

from minet.cli.fetch import fetch_action

SUBPARSERS = {}


def main():
    parser = ArgumentParser(prog='minet')
    subparsers = parser.add_subparsers(
        help='action to execute', title='actions', dest='action')

    fetch_subparser = subparsers.add_parser(
        'fetch', description='Fetches the HTML of the urls of a given CSV column.')
    fetch_subparser.add_argument('column', help='column of the csv file containing urls to fetch')
    fetch_subparser.add_argument(
        'file', help='csv file containing the urls to fetch', type=FileType('r'), default=sys.stdin, nargs='?')

    SUBPARSERS['fetch'] = fetch_subparser

    # facebook_subparser = subparsers.add_parser(
    #     'facebook', description='Adds the Facebook share count for each url of a given CSV column.')
    # facebook_subparser.add_argument('column', help='column')
    # facebook_subparser.add_argument(
    #     'file', help='csv file containing the urls to fetch shares from', type=FileType('r'), default=sys.stdin, nargs='?')
    # facebook_subparser.add_argument(
    #     '-o', '--output', help='output file', type=FileType('w'), default=sys.stdout)
    # SUBPARSERS['facebook'] = facebook_subparser

    # extract_content_subparser = subparsers.add_parser(
    #     'extract_content', description='Return the text content of the urls of a given csv')
    # extract_content_subparser.add_argument(
    #     '--monitoring-file', help='csv monitoring file containing the urls to extract content from', type=FileType('r'), default=join('data', 'monitoring.csv'), nargs='?')
    # extract_content_subparser.add_argument(
    #     '-s', '--storage-location', help='HTML & text storage location', default='data')
    # extract_content_subparser.add_argument(
    #     '-o', '--output', help='output file', type=FileType('w'), default=sys.stdout)
    # SUBPARSERS['extract'] = facebook_subparser

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
