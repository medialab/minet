# =============================================================================
# Minet Argparse Helpers
# =============================================================================
#
# Miscellaneous helpers related to CLI argument parsing.
#
import os
import sys
from os.path import isdir
from io import TextIOBase
from argparse import Action, ArgumentError, ArgumentTypeError
from gettext import gettext
from casanova.utils import CsvRowIO
from tqdm.contrib import DummyTqdmFile
from casanova import Resumer, CsvCellIO
from ebbe import getpath
from datetime import datetime

from minet.cli.exceptions import NotResumable
from minet.cli.utils import acquire_cross_platform_stdout, was_piped_something


class TimestampType(object):
    def __call__(self, date):
        try:
            timestamp = int(datetime.strptime(date, "%Y-%m-%d").timestamp())
        except ValueError:
            raise ArgumentTypeError('UTC date should have the following format : %Y-%m-%d')
        return timestamp


FIVE_YEARS_IN_SEC = 5 * 365.25 * 24 * 60 * 60


class BuzzSumoDateType(object):
    def __call__(self, date):
        try:
            timestamp = int(datetime.strptime(date, "%Y-%m-%d").timestamp())
        except ValueError:
            raise ArgumentTypeError('dates should have the following format : YYYY-MM-DD.')

        if (datetime.now().timestamp() - timestamp) > FIVE_YEARS_IN_SEC:
            raise ArgumentTypeError('you cannot query BuzzSumo using dates before 5 years ago.')

        return timestamp


class SplitterType(object):
    def __init__(self, splitchar=','):
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
        setattr(cli_args, self.dest, False if option_string.startswith('--no') else True)


class InputFileAction(Action):
    def __init__(self, option_strings, dest, dummy_csv_column=None,
                 dummy_csv_columns=None, dummy_csv_guard=None, dummy_csv_error='',
                 column_dest='column', column_dests=None,
                 nargs='?', **kwargs):

        if dummy_csv_guard is not None and not callable(dummy_csv_guard):
            raise TypeError

        self.dummy_csv_column = dummy_csv_column
        self.dummy_csv_columns = dummy_csv_columns
        self.dummy_csv_guard = dummy_csv_guard
        self.dummy_csv_error = dummy_csv_error
        self.column_dest = column_dest
        self.column_dests = column_dests

        if self.dummy_csv_columns is not None:
            assert isinstance(self.column_dests, list) and len(self.dummy_csv_columns) == len(self.column_dests)

        super().__init__(
            option_strings,
            dest,
            default=None,
            nargs=nargs,
            **kwargs
        )

    def __call__(self, parser, cli_args, value, option_string=None):
        setattr(cli_args, 'has_dummy_csv', False)

        if value is None:
            f = sys.stdin

            # No stdin was piped and we have a "dummy" csv file to build
            if not was_piped_something():
                if self.dummy_csv_column is not None:
                    # NOTE: this only work because we are considering positional arguments
                    value = getattr(cli_args, self.column_dest)

                    if self.dummy_csv_guard is not None and not self.dummy_csv_guard(value):
                        raise ArgumentError(self, self.dummy_csv_error + (' Got "%s"' % value))

                    f = CsvCellIO(self.dummy_csv_column, value)
                    setattr(cli_args, self.column_dest, self.dummy_csv_column)
                    setattr(cli_args, 'has_dummy_csv', True)

                elif self.dummy_csv_columns is not None:
                    # NOTE: this only work because we are considering positional arguments
                    values = [getattr(cli_args, dest) for dest in self.column_dests]

                    f = CsvRowIO(self.dummy_csv_columns, values)

                    for i, dest in enumerate(self.column_dests):
                        setattr(cli_args, dest, self.dummy_csv_columns[i])

                    setattr(cli_args, 'has_dummy_csv', True)
        else:
            try:
                f = open(value, 'r', encoding='utf-8')
            except OSError as e:
                args = {'filename': value, 'error': e}
                message = gettext('can\'t open \'%(filename)s\': %(error)s')
                raise ArgumentError(self, message % args)

        setattr(cli_args, self.dest, f)


class OutputFileOpener(object):
    def __init__(self, path=None, resumer_class=None, resumer_kwargs={}, stdout_fallback=True):
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

        mode = 'a' if resume else 'w'

        # As per #254: newline='' is necessary for CSV output on windows to avoid
        # outputting extra lines because of a '\r\r\n' end of line...
        return open(self.path, mode, encoding='utf-8', newline='')


DEFAULT_OUTPUT_FILE_HELP = 'Path to the output file. By default, the results will be printed to stdout.'


class OutputFileAction(Action):
    def __init__(self, option_strings, dest, resumer=None, resumer_kwargs={},
                 help=DEFAULT_OUTPUT_FILE_HELP, stdout_fallback=True, **kwargs):
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
                stdout_fallback=stdout_fallback
            ),
            **kwargs
        )

    def __call__(self, parser, cli_args, value, option_string=None):
        opener = OutputFileOpener(
            value,
            resumer_class=self.resumer,
            resumer_kwargs=self.resumer_kwargs,
            stdout_fallback=self.stdout_fallback
        )
        setattr(cli_args, self.dest, opener)


def rc_key_to_env_var(key):
    return 'MINET_%s' % '_'.join(token.upper() for token in key)


class WrappedConfigValue(object):
    def __init__(self, key, default, _type):
        self.key = key
        self.default = default
        self.type = _type

    def resolve(self, config):

        # Attempting to resolve env variable
        env_var = rc_key_to_env_var(self.key)
        env_value = os.environ.get(env_var, '').strip()

        if env_value:
            return self.type(env_value)

        return getpath(config, self.key, self.default)


class ConfigAction(Action):
    def __init__(self, option_strings, dest, rc_key, default=None, **kwargs):
        if 'help' in kwargs:
            kwargs['help'] = kwargs['help'].rstrip('.') + '. Can also be configured in a .minetrc file as "%s" or read from the %s env variable.' % (
                '.'.join(rc_key),
                rc_key_to_env_var(rc_key)
            )

        super().__init__(
            option_strings,
            dest,
            default=WrappedConfigValue(
                rc_key,
                default,
                kwargs.get('type', str)
            ),
            **kwargs
        )

    def __call__(self, parser, cli_args, values, option_string=None):
        setattr(cli_args, self.dest, values)


def resolve_arg_dependencies(cli_args, config):
    to_close = []

    # Validation
    if getattr(cli_args, 'resume', False) and cli_args.output.path is None:
        raise NotResumable

    # Unwrapping values
    for name in vars(cli_args):
        value = getattr(cli_args, name)

        # Solving wrapped config values
        if isinstance(value, WrappedConfigValue):
            setattr(cli_args, name, value.resolve(config))

        # Opening output files
        if isinstance(value, OutputFileOpener):
            value = value.open(cli_args, resume=getattr(cli_args, 'resume', False))
            setattr(cli_args, name, value)

        # Finding buffers to close eventually
        if (
            (
                isinstance(value, TextIOBase) and
                value is not sys.stdin and
                value is not sys.stdout and
                value is not sys.stderr
            ) or
            isinstance(value, Resumer)
        ):
            to_close.append(value)

    return to_close
