# =============================================================================
# Minet Argparse Helpers
# =============================================================================
#
# Miscellaneous helpers related to CLI argument parsing.
#
from argparse import Action, ArgumentTypeError

from minet.crowdtangle.constants import CROWDTANGLE_PARTITION_STRATEGIES


class BooleanAction(Action):
    """
    Custom argparse action to handle --no-* flags.
    Taken from: https://thisdataguy.com/2017/07/03/no-options-with-argparse-and-python/
    """
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(BooleanAction, self).__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, False if option_string.startswith('--no') else True)


class CrowdtanglePartitionStrategyType(object):
    def __call__(string):
        if string in CROWDTANGLE_PARTITION_STRATEGIES:
            return string

        try:
            return int(string)
        except ValueError:
            choices = ' or '.join(CROWDTANGLE_PARTITION_STRATEGIES)

            raise ArgumentTypeError('partition strategy should either be %s, or an number of posts.' % choices)
