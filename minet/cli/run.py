#!/usr/bin/env python
# =============================================================================
# Minet CLI Endpoint
# =============================================================================
#
# CLI enpoint of the Minet library.
#
import csv
import sys
import ctypes
import importlib
import multiprocessing
import casanova
from casanova.exceptions import EmptyFileError
from contextlib import ExitStack
from encodings import idna  # NOTE: this is necessary for pyinstaller build

from minet.cli.constants import DEFAULT_PREBUFFER_BYTES
from minet.loggers import sleepers_logger
from minet.cli.utils import (
    die,
    get_rcfile,
    CLIRetryerHandler,
    with_cli_exceptions,
)
from minet.cli.argparse import resolve_arg_dependencies, build_parser, get_subparser
from minet.cli.exceptions import NotResumableError, InvalidArgumentsError, FatalError


@with_cli_exceptions
def run(name, version, commands):
    # Freezing multiprocessing support for pyinstaller etc.
    multiprocessing.freeze_support()

    # Increasing max CSV file limit to avoid pesky issues
    csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

    # Casanova global defaults
    casanova.set_default_prebuffer_bytes(DEFAULT_PREBUFFER_BYTES)
    casanova.set_default_ignore_null_bytes(True)

    # Adding handlers for sleepers
    sleepers_logger.addHandler(CLIRetryerHandler())

    # Building parser
    parser, subparser_index = build_parser(name, version, commands)

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
        config = get_rcfile(cli_args.rcfile) if hasattr(cli_args, "rcfile") else None

        # Resolving namespace dependencies
        try:
            to_close = resolve_arg_dependencies(cli_args, config)
        except OSError as e:
            parser.error("Could not open output file (-o/--output): %s" % str(e))
        except InvalidArgumentsError as e:
            parser.error(e.message)
        except NotResumableError:
            parser.error(
                "Cannot --resume without knowing where the output will be written (use -o/--output)"
            )

        # Lazy loading module for faster startup
        meta = action["command"]

        if hasattr(cli_args, "subcommand") and cli_args.subcommand:
            meta = action["command"]["subparsers"]["commands"][cli_args.subcommand]

        if "validate" in meta:
            try:
                meta["validate"](cli_args)
            except InvalidArgumentsError as e:
                parser.error(e.message)

        fn = meta["package"]

        # Lazy-loading
        if not callable(fn):
            m = importlib.import_module(meta["package"])
            fn = getattr(m, "action")

        with ExitStack() as stack:
            for buffer in to_close:
                stack.callback(buffer.close)

            try:
                fn(cli_args)
            except InvalidArgumentsError as e:
                parser.error(e.message)
            except EmptyFileError as e:
                die("Some empty CSV file was given to the command!")
            except FatalError as e:
                die(e.message)

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
