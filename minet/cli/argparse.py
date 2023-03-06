# =============================================================================
# Minet Argparse Helpers
# =============================================================================
#
# Miscellaneous helpers related to CLI argument parsing.
#
from typing import Optional
from typing_extensions import TypedDict, NotRequired

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
    RawDescriptionHelpFormatter,
)
from gettext import gettext
from textwrap import dedent
from casanova import Resumer, CsvCellIO
from ebbe import getpath, omit
from datetime import datetime
from pytz import timezone
from pytz.exceptions import UnknownTimeZoneError

from minet.cli.exceptions import NotResumableError, InvalidArgumentsError
from minet.cli.utils import acquire_cross_platform_stdout

TEMPLATE_RE = re.compile(r"<%\s+([A-Za-z/\-]+)\s+%>")

ARGUMENT_PREFIXES_TO_NORMALIZE = ["--dont-", "--no-", "--", "-"]
FLAG_SORTING_PRIORITIES = {
    name: i
    for i, name in enumerate(
        [
            "select",
            "total",
            "input",
            "output",
            "resume",
            "rcfile",
            "help",
        ],
        1,
    )
}


def normalize_argument_name(name: str) -> str:
    for prefix in ARGUMENT_PREFIXES_TO_NORMALIZE:
        if name.startswith(prefix):
            return name[len(prefix) :]

    return name


def arguments_sort_key(option_strings):
    if not option_strings:
        return (0, 0)

    longest_name = max(option_strings, key=len)
    longest_name = normalize_argument_name(longest_name)

    # Special flags that are dragged down
    priority = FLAG_SORTING_PRIORITIES.get(longest_name, 0)

    return (priority, longest_name)


class SortingRawTextHelpFormatter(RawDescriptionHelpFormatter):
    def add_arguments(self, actions) -> None:
        actions = sorted(actions, key=lambda a: arguments_sort_key(a.option_strings))
        return super().add_arguments(actions)


def custom_formatter(prog):
    terminal_size = shutil.get_terminal_size()

    return SortingRawTextHelpFormatter(
        prog, width=terminal_size.columns, max_help_position=32
    )


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

        if "action" in argument and argument["action"] is ConfigAction:
            try:
                subparser.add_argument(
                    "--rcfile",
                    help="Custom path to a minet configuration file. More info about this here: https://github.com/medialab/minet/blob/master/docs/cli.md#minetrc",
                )
            except ArgumentError:
                pass


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


class DummyCSVInput(object):
    ...


class SingleColumnDummyCSVInput(DummyCSVInput):
    def __init__(self, column, dest):
        self.column = column
        self.dest = dest

    def resolve(self, cli_args):
        value = getattr(cli_args, self.dest)
        f = CsvCellIO(value, column=self.column)
        setattr(cli_args, self.dest, self.column)
        setattr(cli_args, "has_dummy_csv", True)

        return f


class InputAction(Action):
    def __init__(
        self,
        option_strings,
        dest,
        dummy_csv_column=None,
        column_dest="column",
        default=None,
        **kwargs,
    ):
        if dummy_csv_column is not None:
            default = SingleColumnDummyCSVInput(dummy_csv_column, column_dest)

        super().__init__(option_strings, dest, default=default, **kwargs)

    def __call__(self, parser, cli_args, value, option_string=None):
        setattr(cli_args, "has_dummy_csv", False)

        if value == "-":
            f = sys.stdin
        else:
            try:
                f = open(value, "r", encoding="utf-8")
            except OSError as e:
                args = {"filename": value, "error": e}
                message = gettext("can't open '%(filename)s': %(error)s")
                raise ArgumentError(self, message % args)

        setattr(cli_args, self.dest, f)


class OutputOpener(object):
    def __init__(self, path, resumer_class=None, resumer_kwargs={}):
        self.path = path
        self.resumer_class = resumer_class
        self.resumer_kwargs = resumer_kwargs

    def open(self, cli_args, resume=False):
        if self.path == "-":
            if resume:
                raise NotResumableError

            return acquire_cross_platform_stdout()

        if resume and self.resumer_class is not None:
            resumer_kwargs = self.resumer_kwargs

            if callable(self.resumer_kwargs):
                resumer_kwargs = self.resumer_kwargs(cli_args)

            return self.resumer_class(self.path, **resumer_kwargs)

        mode = "a" if resume else "w"

        # As per #254: newline='' is necessary for CSV output on windows to avoid
        # outputting extra lines because of a '\r\r\n' end of line...
        return open(self.path, mode, encoding="utf-8", newline="")


class OutputAction(Action):
    def __init__(
        self,
        option_strings,
        dest,
        resumer=None,
        resumer_kwargs={},
        help="Path to the output file. Will consider `-` as stdout. If not given, results will also be printed to stdout.",
        default="-",
        **kwargs,
    ):
        self.resumer = resumer
        self.resumer_kwargs = resumer_kwargs
        super().__init__(
            option_strings,
            dest,
            help=help,
            default=OutputOpener(
                path=default, resumer_class=resumer, resumer_kwargs=resumer_kwargs
            ),
            **kwargs,
        )

    def __call__(self, parser, cli_args, value, option_string=None):
        opener = OutputOpener(
            path=value,
            resumer_class=self.resumer,
            resumer_kwargs=self.resumer_kwargs,
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
        **kwargs,
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
            **kwargs,
        )

    def __call__(self, parser, cli_args, values, option_string=None):
        if self.plural:
            self.list_values.append(values)
            setattr(cli_args, self.dest, self.list_values)
        else:
            setattr(cli_args, self.dest, values)


def resolve_arg_dependencies(cli_args, config):
    to_close = []

    # Unwrapping values
    # NOTE: I copy the dict from vars because we are going to add new
    # attributes from within the loop
    for name in vars(cli_args).copy():
        value = getattr(cli_args, name)

        # Solving wrapped config values
        if isinstance(value, WrappedConfigValue):
            setattr(cli_args, name, value.resolve(config))

        # Resolving dummy csv input files
        if isinstance(value, DummyCSVInput):
            value = value.resolve(cli_args)
            setattr(cli_args, name, value)

        # Opening output files
        if isinstance(value, OutputOpener):
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


class VariadicInputDefinition(TypedDict):
    dummy_column: str
    item_label: NotRequired[str]
    item_label_plural: NotRequired[str]
    column_help: NotRequired[str]
    input_help: NotRequired[str]


def resolve_typical_arguments(
    args,
    no_output=False,
    resumer=None,
    resumer_kwargs=None,
    select: bool = False,
    total: bool = False,
    variadic_input: Optional[VariadicInputDefinition] = None,
):
    args = [] if args is None else args.copy()
    epilog_addendum = None

    output_argument = {"flags": ["-o", "--output"], "action": OutputAction}

    if variadic_input is not None:
        variadic_input = variadic_input.copy()

        if "column_help" not in variadic_input:
            if "item_label" not in variadic_input:
                variadic_input["item_label"] = variadic_input["dummy_column"]

            if "item_label_plural" not in variadic_input:
                variadic_input["item_label_plural"] = variadic_input["item_label"] + "s"

            variadic_input["column_help"] = (
                "Single %(singular)s to process or name of the CSV column containing %(plural)s when using -i/--input."
                % {
                    "singular": variadic_input["item_label"],
                    "plural": variadic_input["item_label_plural"],
                }
            )
            variadic_input["input_help"] = (
                "CSV file containing all the %s you want to process. Will consider `-` as stdin."
                % variadic_input["item_label_plural"]
            )

        args.append(
            {
                "name": "column",
                "metavar": "value_or_column_name",
                "help": variadic_input["column_help"],
            }
        )

        input_argument = {
            "flags": ["-i", "--input"],
            "help": variadic_input["input_help"],
            "action": InputAction,
            "dummy_csv_column": variadic_input["dummy_column"],
        }

        args.append(input_argument)

        epilog_addendum = """
        how to use the command with a CSV file?

        > A lot of minet commands, including this one, can both be
        > given a single value to process or a bunch of them if
        > given the column of a CSV file passed to -i/--input instead.

        . Here is how to use a command with a single value:
            $ minet cmd "value"

        . Here is how to use a command with a csv file:
            $ minet cmd column_name -i file.csv

        . Here is how to read CSV file from stdin using `-`:
            $ xsv search -s col . | minet cmd column_name -i -
        """

    if select:

        # TODO: actually one can use xsv mini dsl here
        args.append(
            {
                "flags": ["-s", "--select"],
                "help": "Columns of input CSV file to include in the output (separated by `,`).",
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

    if not no_output:
        args.append(output_argument)

    return args, epilog_addendum


def command(
    name: str,
    package=None,
    title: str = None,
    aliases=None,
    description=None,
    epilog=None,
    common_arguments=None,
    arguments=None,
    subcommands=None,
    resolve=None,
    resumer=None,
    resumer_kwargs=None,
    no_output=False,
    select=False,
    total=False,
    variadic_input: Optional[VariadicInputDefinition] = None,
    **kwargs,
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
        data["arguments"], epilog_addendum = resolve_typical_arguments(
            arguments,
            no_output=no_output,
            resumer=resumer,
            resumer_kwargs=resumer_kwargs,
            select=select,
            total=total,
            variadic_input=variadic_input,
        )

        if epilog_addendum is not None:
            if not "epilog" in data:
                data["epilog"] = epilog_addendum
            else:
                data["epilog"] += "\n\n" + epilog_addendum

    if resolve is not None:
        data["resolve"] = resolve

    data.update(kwargs)

    return data


def subcommand(
    name,
    package,
    title,
    description=None,
    epilog=None,
    arguments=[],
    resolve=None,
    resumer=None,
    resumer_kwargs=None,
    no_output=False,
    select=False,
    total=False,
    variadic_input: Optional[VariadicInputDefinition] = None,
    **kwargs,
):
    data = {"name": name, "title": title, "package": package, "arguments": arguments}

    if description is not None:
        data["description"] = description

    if epilog is not None:
        data["epilog"] = epilog

    data["arguments"], epilog_addendum = resolve_typical_arguments(
        arguments,
        no_output=no_output,
        resumer=resumer,
        resumer_kwargs=resumer_kwargs,
        select=select,
        total=total,
        variadic_input=variadic_input,
    )

    if epilog_addendum is not None:
        if not "epilog" in data:
            data["epilog"] = epilog_addendum
        else:
            data["epilog"] += "\n\n" + epilog_addendum

    if resolve is not None:
        data["resolve"] = resolve

    data.update(kwargs)

    return data


def template_readme(tpl, commands):
    _, subparser_index = build_parser("", "", commands)

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
            % target.format_help().strip()
        ).strip()

    return re.sub(TEMPLATE_RE, replacer, tpl)
