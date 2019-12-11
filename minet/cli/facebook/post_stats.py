# =============================================================================
# Minet Facebook Post Stats CLI Action
# =============================================================================
#
# Logic of the `fb post-stats` action.
#
import re
import json5
from tqdm import tqdm

from minet.utils import create_pool, request
from minet.cli.utils import open_output_file, CSVEnricher
from minet.cli.facebook.utils import grab_facebook_cookie

EXTRACTOR_TEMPLATE = rb'\(function\(\)\{bigPipe\.onPageletArrive\((\{allResources:.+share_fbid:"%s".+\})\);\}\),"onPageletArrive'

REPORT_HEADERS = []


# TODO: integrate to ural
def is_facebook_post_url(url):
    return '/posts/' in url or '/permalink/' in url


def facebook_post_stats_action(namespace):

    # Grabbing cookie
    cookie = grab_facebook_cookie(namespace)

    # Handling output
    output_file = open_output_file(namespace.output)

    enricher = CSVEnricher(
        namespace.file,
        namespace.column,
        output_file,
        REPORT_HEADERS,
        select=namespace.select.split(',') if namespace.select else None
    )

    http = create_pool()

    def fetch_facebook_page(url):
        err, response = request(http, url, cookie=cookie)

        if err:
            raise err

        html = response.data

        # TODO: integrate into ural
        post_id = url.rsplit('/', 1)[-1]
        extractor = re.compile(EXTRACTOR_TEMPLATE % post_id.encode())

        match = extractor.search(html)

        if match is None:
            return

        data = json5.loads(match.group(1).decode())
        from pprint import pprint
        pprint(data)

    first_line = next(line for line in enricher if is_facebook_post_url(line[enricher.pos]))

    fetch_facebook_page(first_line[enricher.pos])
