# =============================================================================
# Minet Argparse Helpers
# =============================================================================
#
# Miscellaneous helpers related to CLI argument parsing.
#
import os
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

        super(ConfigAction, self).__init__(
            option_strings,
            dest,
            default=WrappedConfigValue(
                rc_key,
                default,
                kwargs.get('type', str)
            ),
            **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
