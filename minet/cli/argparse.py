# =============================================================================
# Minet Argparse Helpers
# =============================================================================
#
# Miscellaneous helpers related to CLI argument parsing.
#
from argparse import Action, ArgumentTypeError

from minet.utils import nested_get


class BooleanAction(Action):
    """
    Custom argparse action to handle --no-* flags.
    Taken from: https://thisdataguy.com/2017/07/03/no-options-with-argparse-and-python/
    """
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(BooleanAction, self).__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, False if option_string.startswith('--no') else True)


class SplitterType(object):
    def __init__(self, splitchar=','):
        self.splitchar = splitchar

    def __call__(self, string):
        return string.split(self.splitchar)


class WrappedConfigValue(object):
    def __init__(self, key, default):
        self.key = key
        self.default = default

    def resolve(self, config):
        return nested_get(self.key, config, self.default)


class ConfigAction(Action):
    def __init__(self, option_strings, dest, rc_key, default=None, **kwargs):
        super(ConfigAction, self).__init__(
            option_strings,
            dest,
            default=WrappedConfigValue(
                rc_key,
                default
            ),
            **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
