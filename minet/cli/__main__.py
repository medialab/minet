#!/usr/bin/env python
# =============================================================================
# Minet CLI Endpoint
# =============================================================================
#
# CLI enpoint of the Minet library.
#
import os
import csv
import sys
import ctypes
import shutil
import importlib
import multiprocessing
import casanova
from textwrap import dedent
from tqdm import tqdm
from contextlib import ExitStack
from argparse import ArgumentParser, RawTextHelpFormatter
from colorama import init as colorama_init
from encodings import idna  # NOTE: this is necessary for pyinstaller build

from minet.__version__ import __version__
from minet.cli.constants import DEFAULT_PREBUFFER_BYTES
from minet.cli.utils import die, get_rcfile
from minet.cli.argparse import resolve_arg_dependencies
from minet.cli.exceptions import NotResumable, InvalidArgumentsError

from minet.cli.commands import MINET_COMMANDS


def custom_formatter(prog):
    terminal_size = shutil.get_terminal_size()

    return RawTextHelpFormatter(prog, max_help_position=50, width=terminal_size.columns)


def omit(d, keys_to_omit):
    nd = {}

    for k, v in d.items():
        if k in keys_to_omit:
            continue

        nd[k] = v

    return nd


def get_subparser(o, keys):
    parser = None

    for key in keys:
        item = o.get(key)

        if item is None:
            return None

        parser = item["parser"]

        if "subparsers" in item:
            o = item["subparsers"]
        else:
            break

    return parser


ARGUMENT_KEYS_TO_OMIT = ["name", "flag", "flags"]


def add_arguments(subparser, arguments):
    for argument in arguments:

        argument_kwargs = omit(argument, ARGUMENT_KEYS_TO_OMIT)

        if "choices" in argument_kwargs:
            argument_kwargs["choices"] = sorted(argument_kwargs["choices"])

        if "name" in argument:
            subparser.add_argument(argument["name"], **argument_kwargs)
        elif "flag" in argument:
            subparser.add_argument(argument["flag"], **argument_kwargs)
        else:
            subparser.add_argument(*argument["flags"], **argument_kwargs)


def build_description(command):
    description = command["title"] + "\n" + ("=" * len(command["title"]))

    text = dedent(command.get("description", ""))
    description += "\n\n" + text

    return description


def build_subparsers(
    parser,
    index,
    commands,
    help="Action to execute",
    title="actions",
    dest="action",
    common_arguments=[],
):

    subparsers = parser.add_subparsers(help=help, title=title, dest=dest)

    for name, command in commands.items():
        subparser = subparsers.add_parser(
            name,
            description=build_description(command),
            epilog=dedent(command.get("epilog", "")),
            formatter_class=custom_formatter,
            aliases=command.get("aliases", []),
        )

        subparser.add_argument(
            "--rcfile", help="Custom path to a minet configuration file."
        )

        to_index = {"parser": subparser, "command": command, "subparsers": {}}

        add_arguments(subparser, common_arguments)

        if "arguments" in command:
            add_arguments(subparser, command["arguments"])

        if "subparsers" in command:
            subsubparsers = command["subparsers"]
            subcommon_arguments = subsubparsers.get("common_arguments", [])

            add_arguments(subparser, subcommon_arguments)

            build_subparsers(
                subparser,
                to_index["subparsers"],
                subsubparsers["commands"],
                help=subsubparsers["help"],
                title=subsubparsers["title"],
                dest=subsubparsers["dest"],
                common_arguments=common_arguments + subcommon_arguments,
            )

        if "aliases" in command:
            for alias in command["aliases"]:
                index[alias] = to_index

        index[name] = to_index

    return subparsers


def build_parser(commands):

    # Building the argument parser
    parser = ArgumentParser(prog="minet")

    parser.add_argument("--version", action="version", version="minet %s" % __version__)

    subparser_index = {}

    subparsers = build_subparsers(parser, subparser_index, commands)

    # Help subparser
    help_subparser = subparsers.add_parser("help")
    help_subparser.add_argument("subcommand", help="Name of the subcommand", nargs="*")

    return parser, subparser_index


def main():

    # Building parser
    parser, subparser_index = build_parser(MINET_COMMANDS)

    # Parsing arguments and triggering commands
    cli_args = parser.parse_args()

    action = subparser_index.get(cli_args.action)

    if action is not None:

        # If subparser is called without any subaction, we print help and exit
        if "subparsers" in action["command"]:
            subdest = action["command"]["subparsers"]["dest"]
            subaction = getattr(cli_args, subdest)

            if subaction is None:
                action["parser"].print_help()
                sys.exit(0)

        # Loading config
        config = get_rcfile(cli_args.rcfile)

        # Resolving namespace dependencies
        try:
            to_close = resolve_arg_dependencies(cli_args, config)
        except OSError as e:
            parser.error("Could not open output file (-o/--output): %s" % str(e))
        except NotResumable:
            parser.error(
                "Cannot --resume without knowing where the output will be written (use -o/--output)"
            )

        # Lazy loading module for faster startup
        m = importlib.import_module(action["command"]["package"])
        fn = getattr(m, action["command"]["action"])

        with ExitStack() as stack:
            for buffer in to_close:
                stack.callback(buffer.close)

            try:
                fn(cli_args)
            except InvalidArgumentsError as e:
                parser.error(e.message)
                sys.exit(1)

    elif cli_args.action == "help":

        if len(cli_args.subcommand) == 0:
            parser.print_help()
            return

        target = get_subparser(subparser_index, cli_args.subcommand)

        if target is None:
            die('Unknow command "%s"' % " ".join(cli_args.subcommand))
        else:
            target.print_help()

    else:
        parser.print_help()


if __name__ == "__main__":
    # Freezing multiprocessing support for pyinstaller etc.
    multiprocessing.freeze_support()

    # Colorama initialization hook
    colorama_init()

    # Increasing max CSV file limit to avoid pesky issues
    csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

    # Casanova global defaults
    casanova.set_default_prebuffer_bytes(DEFAULT_PREBUFFER_BYTES)
    casanova.set_default_ignore_null_bytes(True)

    try:
        main()

    except BrokenPipeError:

        # Taken from: https://docs.python.org/3/library/signal.html
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)

    except KeyboardInterrupt:

        # Cleaning up tqdm loading bar nicely on keyboard interrupts
        for bar in list(tqdm._instances):
            bar.leave = False
            bar.close()

        sys.exit(1)
