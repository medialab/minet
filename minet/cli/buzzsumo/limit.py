# =============================================================================
# Minet BuzzSumo Limit CLI Action
# =============================================================================
#
# Logic of the `bz limit` action.
#
from termcolor import colored

from minet.utils import prettyprint_integer
from minet.buzzsumo.utils import URL_TEMPLATE, call_buzzsumo_once


def buzzsumo_limit_action(cli_args):

    url = URL_TEMPLATE % cli_args.token + '&q=fake%20news'

    _, headers = call_buzzsumo_once(url)

    print(
        'With your token, you can still make',
        colored(prettyprint_integer(headers['X-RateLimit-Month-Remaining']), 'green'),
        'calls to the BuzzSumo API until the end of the month.'
    )
