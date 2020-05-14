# =============================================================================
# Minet Twitter Friends CLI Action
# =============================================================================
#
# Logic of the `tw friends` action.
#
import time
import sys, json
from minet.utils import create_pool, request_json
from minet.cli.utils import CSVEnricher, die
from minet.twitter.utils import TwitterWrapper
from twitter import *

REPORT_HEADERS = [
    'friends_id'
]

def twitter_friends_action(namespace, output_file):

    TWITTER = {
        'OAUTH_TOKEN' : namespace.access_token,
        'OAUTH_SECRET' : namespace.access_token_secret,
        'KEY' : namespace.api_key,
        'SECRET' : namespace.api_secret_key
    }

    wrapper = TwitterWrapper(TWITTER)

    enricher = CSVEnricher(
        namespace.file,
        namespace.column,
        output_file,
        report_headers=REPORT_HEADERS,
        select=namespace.select.split(',') if namespace.select else None
    )

    for row in enricher:
        user_id = row[enricher.pos]
        all_ids = []

        result = wrapper.call('friends.ids', args={'user_id': user_id})
        all_ids = result.get('ids', None)

        for id in all_ids:
            enricher.write(row, [id])


