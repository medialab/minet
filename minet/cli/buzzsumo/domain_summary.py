# =============================================================================
# Minet BuzzSumo Domain Summary CLI Action
# =============================================================================
#
# Logic of the `bz domain-summary` action.
#
from minet.web import request_json


URL_TEMPLATE = 'https://api.buzzsumo.com/search/articles.json?api_key=%s&q=%s'


def buzzsumo_domain_summary_action(cli_args):
    print('test', cli_args.token)