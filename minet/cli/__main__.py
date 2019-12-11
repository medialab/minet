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
import multiprocessing
from textwrap import dedent
from argparse import (
    ArgumentParser,
    RawTextHelpFormatter
)

from minet.__version__ import __version__
from minet.cli.utils import die

from minet.cli.commands import MINET_COMMANDS

# Handling pipes correctly
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

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


def build_subparsers(parser, index, commands, help='Action to execute', title='actions',
                     dest='action', common_arguments=[]):

    subparser_index = {}

    subparsers = parser.add_subparsers(
        help=help,
        title=title,
        dest=dest
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

        add_arguments(subparser, common_arguments)

        if 'arguments' in command:
            add_arguments(subparser, command['arguments'])

        if 'subparsers' in command:
            subsubparsers = command['subparsers']
            subcommon_arguments = subsubparsers.get('common_arguments', [])

            add_arguments(subparser, subcommon_arguments)

            build_subparsers(
                subparser,
                to_index['subparsers'],
                subsubparsers['commands'],
                help=subsubparsers['help'],
                title=subsubparsers['title'],
                dest=subsubparsers['dest'],
                common_arguments=common_arguments + subcommon_arguments
            )

        if 'aliases' in command:
            for alias in command['aliases']:
                index[alias] = to_index

        index[name] = to_index

    return subparsers


def build_parser(commands):

    # Building the argument parser
    parser = ArgumentParser(prog='minet')

    parser.add_argument('--version', action='version', version='minet %s' % __version__)

    subparser_index = {}

    subparsers = build_subparsers(parser, subparser_index, commands)

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

        if len(args.subcommand) == 0:
            parser.print_help()
            return

        target = get_subparser(subparser_index, args.subcommand)

        if target is None:
            die('Unknow command "%s"' % ' '.join(args.subcommand))
        else:
            target.print_help()

    else:
        parser.print_help()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
