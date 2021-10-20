# =============================================================================
# Minet BuzzSumo Limit CLI Action
# =============================================================================
#
# Logic of the `bz limit` action.
#
from termcolor import colored

from minet.web import request_json


URL_TEMPLATE = 'https://api.buzzsumo.com/search/articles.json?api_key=%s&q=%s'


def buzzsumo_limit_action(cli_args):

    err, response, data = request_json(URL_TEMPLATE % (cli_args.token, 'fake%20news'))

    if err:
        print(colored('Error', 'red'), err)
    else:
        if response.status == 200:
            print(
                'With your token, you can still make',
                colored(response.headers['X-RateLimit-Month-Remaining'], 'green'),
                'calls to the BuzzSumo API until the end of the month.'
            )
        else:
            print(colored('Error', 'red'), response.status)
            if data:
                print(data)
