#!/usr/bin/env python
# =============================================================================
# Minet CLI Endpoint
# =============================================================================
#
# CLI enpoint of the Minet library.
#
import csv
import sys
import signal
import shutil
import importlib
from textwrap import dedent
from argparse import (
    ArgumentParser,
    RawTextHelpFormatter
)

from minet.__version__ import __version__
from minet.cli.utils import die

from minet.cli.commands import MINET_COMMANDS

SUBPARSERS = {}

# Getting terminal size
terminal_size = shutil.get_terminal_size()

# Increasing max CSV file limit to avoid pesky issues
csv.field_size_limit(sys.maxsize)

# Hiding stack traces on ctrl+c
signal.signal(signal.SIGINT, lambda x, y: sys.exit(1))


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


def get_subparser(o, keys):
    parser = None

    for key in keys:
        item = o.get(key)

        if item is None:
            return None

        parser = item['parser']

        if 'subparsers' in item:
            o = item['subparsers']
        else:
            break

    return parser


def add_arguments(subparser, arguments):
    for argument in arguments:
        if 'name' in argument:
            subparser.add_argument(argument['name'], **omit(argument, 'name'))
        elif 'flag' in argument:
            subparser.add_argument(argument['flag'], **omit(argument, 'flag'))
        else:
            subparser.add_argument(*argument['flags'], **omit(argument, 'flags'))


def build_description(command):
    description = command['title'] + '\n' + ('=' * len(command['title']))

    description += '\n\n' + dedent(command.get('description', ''))

    return description


def build_parser(commands):

    # Building the argument parser
    parser = ArgumentParser(prog='minet')

    parser.add_argument('--version', action='version', version='minet %s' % __version__)

    subparser_index = {}

    subparsers = parser.add_subparsers(
        help='Action to execute',
        title='actions',
        dest='action'
    )

    for name, command in commands.items():
        subparser = subparsers.add_parser(
            name,
            description=build_description(command),
            epilog=dedent(command.get('epilog', '')),
            formatter_class=custom_formatter,
            aliases=command.get('aliases', [])
        )

        to_index = {
            'parser': subparser,
            'command': command,
            'subparsers': {}
        }

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
                    description=build_description(subcommand),
                    epilog=dedent(subcommand.get('epilog', '')),
                    formatter_class=custom_formatter
                )

                if common_arguments:
                    add_arguments(subsubparser, common_arguments)

                if 'arguments' in subcommand:
                    add_arguments(subsubparser, subcommand['arguments'])

                to_index['subparsers'][subname] = {
                    'parser': subsubparser
                }

        if 'aliases' in command:
            for alias in command['aliases']:
                subparser_index[alias] = to_index

        subparser_index[name] = to_index

    # Help subparser
    help_subparser = subparsers.add_parser('help')
    help_subparser.add_argument('subcommand', help='Name of the subcommand', nargs='*')

    return parser, subparser_index


def main():

    # Building parser
    parser, subparser_index = build_parser(MINET_COMMANDS)

    # Parsing arguments and triggering commands
    args = parser.parse_args()

    action = subparser_index.get(args.action)

    if action is not None:

        # Need to check something?
        if 'before' in action['command']:
            action['command']['before']()

        # Lazy loading module for faster startup
        m = importlib.import_module(action['command']['package'])
        fn = getattr(m, action['command']['action'])

        fn(args)

    elif args.action == 'help':
        target = get_subparser(subparser_index, args.subcommand)

        if target is None:
            die('Unknow command "%s"' % ' '.join(args.subcommand))
        else:
            target.print_help()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
