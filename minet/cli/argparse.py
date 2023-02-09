# =============================================================================
# Minet Argparse Helpers
# =============================================================================
#
# Miscellaneous helpers related to CLI argument parsing.
#
import os
import re
import sys
import shutil
from os.path import isdir
from io import TextIOBase
from argparse import (
    Action,
    ArgumentError,
    ArgumentTypeError,
    ArgumentParser,
    RawTextHelpFormatter,
)
from gettext import gettext
from textwrap import dedent
from tqdm.contrib import DummyTqdmFile
from casanova import Resumer, CsvCellIO, CsvRowIO
from ebbe import getpath, omit
from datetime import datetime
from pytz import timezone
from pytz.exceptions import UnknownTimeZoneError

from minet.cli.exceptions import NotResumableError, InvalidArgumentsError
from minet.cli.utils import acquire_cross_platform_stdout, was_piped_something

TEMPLATE_RE = re.compile(r"<%\s+([A-Za-z/\-]+)\s+%>")


def custom_formatter(prog):
    terminal_size = shutil.get_terminal_size()

    return RawTextHelpFormatter(prog, max_help_position=50, width=terminal_size.columns)


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


def build_parser(name, version, commands):

    # Building the argument parser
    parser = ArgumentParser(prog="minet")

    parser.add_argument(
        "--version", action="version", version="%s %s" % (name, version)
    )

    subparser_index = {}

    subparsers = build_subparsers(
        parser, subparser_index, {c["name"]: c for c in commands}
    )

    # Help subparser
    help_subparser = subparsers.add_parser("help")
    help_subparser.add_argument("subcommand", help="Name of the subcommand", nargs="*")

    return parser, subparser_index


class TimestampType(object):
    def __call__(self, date):
        try:
            timestamp = int(datetime.strptime(date, "%Y-%m-%d").timestamp())
        except ValueError:
            raise ArgumentTypeError(
                "UTC date should have the following format : %Y-%m-%d"
            )
        return timestamp


class TimezoneType(object):
    def __call__(self, locale):
        try:
            tz = timezone(locale)
        except UnknownTimeZoneError:
            raise ArgumentTypeError("This timezone is not recognized.")
        return tz


class SplitterType(object):
    def __init__(self, splitchar=","):
        self.splitchar = splitchar

    def __call__(self, string):
        return string.split(self.splitchar)


class ExistingDirectoryType(object):
    def __call__(self, string):
        if not isdir(string):
            raise ArgumentTypeError('Could not find the "%s" directory!' % string)


class BooleanAction(Action):
    """
    Custom argparse action to handle --no-* flags.
    Taken from: https://thisdataguy.com/2017/07/03/no-options-with-argparse-and-python/
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, cli_args, values, option_string=None):
        setattr(
            cli_args,
            self.dest,
            False
            if (
                option_string.startswith("--no-") or option_string.startswith("--dont-")
            )
            else True,
        )


class InputFileAction(Action):
    def __init__(
        self,
        option_strings,
        dest,
        dummy_csv_column=None,
        dummy_csv_columns=None,
        dummy_csv_guard=None,
        dummy_csv_error="",
        column_dest="column",
        column_dests=None,
        nargs="?",
        **kwargs
    ):

        if dummy_csv_guard is not None and not callable(dummy_csv_guard):
            raise TypeError

        self.dummy_csv_column = dummy_csv_column
        self.dummy_csv_columns = dummy_csv_columns
        self.dummy_csv_guard = dummy_csv_guard
        self.dummy_csv_error = dummy_csv_error
        self.column_dest = column_dest
        self.column_dests = column_dests

        if self.dummy_csv_columns is not None:
            assert isinstance(self.column_dests, list) and len(
                self.dummy_csv_columns
            ) == len(self.column_dests)

        super().__init__(option_strings, dest, default=None, nargs=nargs, **kwargs)

    def __call__(self, parser, cli_args, value, option_string=None):
        setattr(cli_args, "has_dummy_csv", False)

        if value is None:
            f = sys.stdin

            # No stdin was piped and we have a "dummy" csv file to build
            if not was_piped_something():
                if self.dummy_csv_column is not None:
                    # NOTE: this only work because we are considering positional arguments
                    value = getattr(cli_args, self.column_dest)

                    if self.dummy_csv_guard is not None and not self.dummy_csv_guard(
                        value
                    ):
                        raise ArgumentError(
                            self, self.dummy_csv_error + (' Got "%s"' % value)
                        )

                    f = CsvCellIO(self.dummy_csv_column, value)
                    setattr(cli_args, self.column_dest, self.dummy_csv_column)
                    setattr(cli_args, "has_dummy_csv", True)

                elif self.dummy_csv_columns is not None:
                    # NOTE: this only work because we are considering positional arguments
                    values = [getattr(cli_args, dest) for dest in self.column_dests]

                    f = CsvRowIO(self.dummy_csv_columns, values)

                    for i, dest in enumerate(self.column_dests):
                        setattr(cli_args, dest, self.dummy_csv_columns[i])

                    setattr(cli_args, "has_dummy_csv", True)
        else:
            try:
                f = open(value, "r", encoding="utf-8")
            except OSError as e:
                args = {"filename": value, "error": e}
                message = gettext("can't open '%(filename)s': %(error)s")
                raise ArgumentError(self, message % args)

        setattr(cli_args, self.dest, f)


class OutputFileOpener(object):
    def __init__(
        self, path=None, resumer_class=None, resumer_kwargs={}, stdout_fallback=True
    ):
        self.path = path
        self.resumer_class = resumer_class
        self.resumer_kwargs = resumer_kwargs
        self.stdout_fallback = stdout_fallback

    def open(self, cli_args, resume=False):
        if self.path is None:
            if not self.stdout_fallback:
                return None

            if resume:
                raise RuntimeError

            return DummyTqdmFile(acquire_cross_platform_stdout())

        if resume and self.resumer_class is not None:
            resumer_kwargs = self.resumer_kwargs

            if callable(self.resumer_kwargs):
                resumer_kwargs = self.resumer_kwargs(cli_args)

            return self.resumer_class(self.path, **resumer_kwargs)

        mode = "a" if resume else "w"

        # As per #254: newline='' is necessary for CSV output on windows to avoid
        # outputting extra lines because of a '\r\r\n' end of line...
        return open(self.path, mode, encoding="utf-8", newline="")


DEFAULT_OUTPUT_FILE_HELP = (
    "Path to the output file. By default, the results will be printed to stdout."
)


class OutputFileAction(Action):
    def __init__(
        self,
        option_strings,
        dest,
        resumer=None,
        resumer_kwargs={},
        help=DEFAULT_OUTPUT_FILE_HELP,
        stdout_fallback=True,
        **kwargs
    ):
        self.resumer = resumer
        self.resumer_kwargs = resumer_kwargs
        self.stdout_fallback = stdout_fallback
        super().__init__(
            option_strings,
            dest,
            help=help,
            default=OutputFileOpener(
                resumer_class=resumer,
                resumer_kwargs=resumer_kwargs,
                stdout_fallback=stdout_fallback,
            ),
            **kwargs
        )

    def __call__(self, parser, cli_args, value, option_string=None):
        opener = OutputFileOpener(
            value,
            resumer_class=self.resumer,
            resumer_kwargs=self.resumer_kwargs,
            stdout_fallback=self.stdout_fallback,
        )
        setattr(cli_args, self.dest, opener)


def rc_key_to_env_var(key):
    return "MINET_%s" % "_".join(token.upper() for token in key)


class WrappedConfigValue(object):
    def __init__(self, flag, key, default, _type, required=False):
        self.flag = flag
        self.key = key
        self.default = default
        self.type = _type
        self.required = required

    def resolve(self, config):
        value = None

        # Attempting to resolve env variable
        env_var = rc_key_to_env_var(self.key)
        env_value = os.environ.get(env_var, "").strip()

        if env_value:
            value = self.type(env_value)
        else:
            value = getpath(config, self.key, self.default)

        if value is None and self.required:
            raise InvalidArgumentsError(
                '%s is mandatory!\nIt can also be given using the %s env variable or using the "%s" .minetrc config key.\nMore info about this here: https://github.com/medialab/minet/blob/master/docs/cli.md#minetrc'
                % ("/".join(self.flag), env_var, ".".join(self.key))
            )

        return value


class ConfigAction(Action):
    def __init__(
        self,
        option_strings,
        dest,
        rc_key,
        default=None,
        plural=False,
        required=False,
        **kwargs
    ):
        if "help" in kwargs:
            kwargs["help"] = kwargs["help"].rstrip(
                "."
            ) + '. Can also be configured in a .minetrc file as "%s" or read from the %s env variable.' % (
                ".".join(rc_key),
                rc_key_to_env_var(rc_key),
            )

        self.plural = plural

        if plural == True:
            self.list_values = []

        super().__init__(
            option_strings,
            dest,
            default=WrappedConfigValue(
                option_strings,
                rc_key,
                default,
                kwargs.get("type", str),
                required=required,
            ),
            **kwargs
        )

    def __call__(self, parser, cli_args, values, option_string=None):
        if self.plural:
            self.list_values.append(values)
            setattr(cli_args, self.dest, self.list_values)
        else:
            setattr(cli_args, self.dest, values)


def resolve_arg_dependencies(cli_args, config):
    to_close = []

    # Validation
    if getattr(cli_args, "resume", False) and cli_args.output.path is None:
        raise NotResumableError

    # Unwrapping values
    for name in vars(cli_args):
        value = getattr(cli_args, name)

        # Solving wrapped config values
        if isinstance(value, WrappedConfigValue):
            setattr(cli_args, name, value.resolve(config))

        # Opening output files
        if isinstance(value, OutputFileOpener):
            value = value.open(cli_args, resume=getattr(cli_args, "resume", False))
            setattr(cli_args, name, value)

        # Finding buffers to close eventually
        if (
            isinstance(value, TextIOBase)
            and value is not sys.stdin
            and value is not sys.stdout
            and value is not sys.stderr
        ) or isinstance(value, Resumer):
            to_close.append(value)

    return to_close


def resolve_typical_arguments(
    args,
    resumer=None,
    resumer_kwargs=None,
    select=False,
    total=False,
    variadic_input=None,
):
    args = [] if args is None else args.copy()

    output_argument = {"flags": ["-o", "--output"], "action": OutputFileAction}

    if variadic_input is not None:
        variadic_input = variadic_input.copy()

        if "column_help" not in variadic_input:
            if "item_label" not in variadic_input:
                variadic_input["item_label"] = variadic_input["dummy_column"]

            if "item_label_plural" not in variadic_input:
                variadic_input["item_label_plural"] = variadic_input["item_label"] + "s"

            variadic_input[
                "column_help"
            ] = "Name of the CSV column containing %s or a single %s." % (
                variadic_input["item_label_plural"],
                variadic_input["item_label"],
            )
            variadic_input["file_help"] = (
                "CSV file containing the %s." % variadic_input["item_label_plural"]
            )

        args.append({"name": "column", "help": variadic_input["column_help"]})

        file_argument = {
            "name": "file",
            "help": variadic_input["file_help"],
            "action": InputFileAction,
            "dummy_csv_column": variadic_input["dummy_column"],
        }

        if "guard" in variadic_input:
            file_argument["dummy_csv_guard"] = variadic_input["guard"]

        if "guard_error_message" in variadic_input:
            file_argument["dummy_csv_error"] = variadic_input["guard_error_message"]

        args.append(file_argument)

    if select:
        args.append(
            {
                "flags": ["-s", "--select"],
                "help": "Columns of input CSV file to include in the output (separated by `,`).",
                "type": SplitterType(),
            },
        )

    if total:
        args.append(
            {
                "flag": "--total",
                "help": "Total number of items to process. Necessary if you want to display a finite progress indicator.",
                "type": int,
            }
        )

    if resumer is not None:
        args.append(
            {
                "flag": "--resume",
                "help": "Whether to resume from an aborted collection. Need -o to be set.",
                "action": "store_true",
            },
        )

        output_argument["resumer"] = resumer

        if resumer_kwargs is not None:
            output_argument["resumer_kwargs"] = resumer_kwargs

    args.append(output_argument)

    return args


def command(
    name,
    package=None,
    title=None,
    aliases=None,
    description=None,
    epilog=None,
    common_arguments=None,
    arguments=None,
    subcommands=None,
    validate=None,
    resumer=None,
    resumer_kwargs=None,
    select=False,
    total=False,
    variadic_input=None,
    **kwargs
):

    if arguments is not None and subcommands is not None:
        raise TypeError(
            "command cannot have subcommands and be executable on its own (avoid giving arguments AND subcommands)"
        )

    data = {"name": name, "title": title}

    if package is not None:
        data["package"] = package

    if aliases is not None:
        data["aliases"] = aliases

    if description is not None:
        data["description"] = description

    if epilog is not None:
        data["epilog"] = epilog

    if subcommands is not None:
        data["subparsers"] = {
            "help": "Subcommand to use.",
            "title": "subcommands",
            "dest": "subcommand",
            "commands": {s["name"]: s for s in subcommands},
        }

        if common_arguments is not None:
            data["subparsers"]["common_arguments"] = common_arguments

    elif arguments is not None:
        data["arguments"] = resolve_typical_arguments(
            arguments,
            resumer=resumer,
            resumer_kwargs=resumer_kwargs,
            select=select,
            total=total,
            variadic_input=variadic_input,
        )

    if validate is not None:
        data["validate"] = validate

    data.update(kwargs)

    return data


def subcommand(
    name,
    package,
    title,
    description=None,
    epilog=None,
    arguments=[],
    validate=None,
    resumer=None,
    resumer_kwargs=None,
    select=False,
    total=False,
    variadic_input=None,
    **kwargs
):
    data = {"name": name, "title": title, "package": package, "arguments": arguments}

    if description is not None:
        data["description"] = description

    if epilog is not None:
        data["epilog"] = epilog

    data["arguments"] = resolve_typical_arguments(
        arguments,
        resumer=resumer,
        resumer_kwargs=resumer_kwargs,
        select=select,
        total=total,
        variadic_input=variadic_input,
    )

    if validate is not None:
        data["validate"] = validate

    data.update(kwargs)

    return data


def template_readme(tpl, commands):
    parser, subparser_index = build_parser("", "", commands)

    def replacer(match):
        keys = match.group(1).split("/")

        target = get_subparser(subparser_index, keys)

        if target is None:
            raise TypeError('missing key "%s"' % "/".join(keys))

        return (
            dedent(
                """
                    ```
                    %s
                    ```
                """
            )
            % target.format_help()
        ).strip()

    return re.sub(TEMPLATE_RE, replacer, tpl)
