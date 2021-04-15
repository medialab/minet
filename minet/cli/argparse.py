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
from tqdm.contrib import DummyTqdmFile
from casanova import Resumer

from minet.utils import nested_get
from minet.cli.exceptions import NotResumable
from minet.cli.utils import (
    acquire_cross_platform_stdout,
    CsvIO
)


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
                 column_dest='column', **kwargs):

        self.dummy_csv_column = dummy_csv_column
        self.column_dest = column_dest

        super().__init__(
            option_strings,
            dest,
            default=None,
            nargs='?',
            **kwargs
        )

    def __call__(self, parser, cli_args, value, option_string=None):
        input_is_dummy_csv = False

        if value is None:
            f = sys.stdin

            if self.dummy_csv_column is not None:

                # No stdin was piped
                if sys.stdin.isatty():
                    f = CsvIO(self.dummy_csv_column, getattr(cli_args, self.column_dest))
                    setattr(cli_args, self.column_dest, self.dummy_csv_column)
                    input_is_dummy_csv = True
        else:
            try:
                f = open(value, 'r', encoding='utf-8')
            except OSError as e:
                args = {'filename': value, 'error': e}
                message = gettext('can\'t open \'%(filename)s\': %(error)s')
                raise ArgumentError(self, message % args)

        setattr(cli_args, self.dest, f)
        setattr(cli_args, 'input_is_dummy_csv', input_is_dummy_csv)


class OutputFileOpener(object):
    def __init__(self, path=None, resumer_class=None, resumer_kwargs={}):
        self.path = path
        self.resumer_class = resumer_class
        self.resumer_kwargs = resumer_kwargs

    def open(self, resume=False):
        if self.path is None:
            if resume:
                raise RuntimeError

            return DummyTqdmFile(acquire_cross_platform_stdout())

        if resume and self.resumer_class is not None:
            return self.resumer_class(self.path, **self.resumer_kwargs)

        mode = 'a' if resume else 'w'

        # As per #254: newline='' is necessary for CSV output on windows to avoid
        # outputting extra lines because of a '\r\r\n' end of line...
        return open(self.path, mode, encoding='utf-8', newline='')


DEFAULT_OUTPUT_FILE_HELP = 'Path to the output file. By default, the results will be printed to stdout.'


class OutputFileAction(Action):
    def __init__(self, option_strings, dest, resumer=None, resumer_kwargs={},
                 help=DEFAULT_OUTPUT_FILE_HELP, **kwargs):
        self.resumer = resumer
        self.resumer_kwargs = resumer_kwargs
        super().__init__(
            option_strings,
            dest,
            help=help,
            default=OutputFileOpener(
                resumer_class=resumer,
                resumer_kwargs=resumer_kwargs
            ),
            **kwargs
        )

    def __call__(self, parser, cli_args, value, option_string=None):
        opener = OutputFileOpener(
            value,
            resumer_class=self.resumer,
            resumer_kwargs=self.resumer_kwargs
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

        return nested_get(self.key, config, self.default)


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
            value = value.open(resume=getattr(cli_args, 'resume', False))
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
