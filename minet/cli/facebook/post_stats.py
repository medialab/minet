# =============================================================================
# Minet Facebook Post Stats CLI Action
# =============================================================================
#
# Logic of the `fb post-stats` action.
#
import re
import json5
import time
from tqdm import tqdm

from minet.utils import create_pool, request, nested_get
from minet.cli.utils import open_output_file, CSVEnricher
from minet.cli.facebook.utils import grab_facebook_cookie
from minet.cli.facebook.constants import FACEBOOK_DEFAULT_THROTTLE

EXTRACTOR_TEMPLATE = rb'\(function\(\)\{bigPipe\.onPageletArrive\((\{allResources:.+share_fbid:"%s".+\})\);\}\),"onPageletArrive'
CURRENT_AVAILABILITY_DISCLAIMER = b'Sorry, this content isn\'t available right now'
AVAILABILITY_DISCLAIMER = b'The link you followed may be broken, or the page may have been removed.'

# TODO: top
REPORT_HEADERS = [
    'error',
    'share_count',
    'comment_count',
    'reaction_count',
    'reactor_count',
    'seen_by_count'
]

ERROR_PADDING = [''] * (len(REPORT_HEADERS) - 1)


# TODO: integrate to ural
def is_facebook_post_url(url):
    return '/posts/' in url or '/permalink/' in url


def get_count(item):
    if item is None:
        return 0

    value = item.get('count')

    if not value:
        value = item.get('total_count')

    return value or 0


def format_err(err):
    return [err] + ERROR_PADDING


def format(data):
    return [
        '',
        get_count(data['share_count']),
        get_count(data['comment_count']),
        get_count(data['reaction_count']),
        get_count(data['reactors']),
        get_count(data['seen_by_count'])
    ]


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

    def fetch_facebook_page_stats(url):
        err, response = request(http, url, cookie=cookie)

        if err:
            return 'http-error', None

        if response.status == 404:
            return 'not-found', None

        if response.status >= 400:
            return 'http-error', None

        html = response.data

        if (
            CURRENT_AVAILABILITY_DISCLAIMER in html or
            AVAILABILITY_DISCLAIMER in html
        ):
            return 'unavailable', None

        # TODO: integrate into ural
        post_id = url.rsplit('/', 1)[-1]
        extractor = re.compile(EXTRACTOR_TEMPLATE % post_id.encode())

        match = extractor.search(html)

        if match is None:
            return 'extraction-failed', None

        data = json5.loads(match.group(1).decode())
        data = nested_get(
            ['jsmods', 'pre_display_requires', 0, 3, 1, '__bbox', 'result', 'data', 'feedback'],
            data
        )

        if data is None:
            return 'extraction-failed', None

        return None, data

    # Loading bar
    loading_bar = tqdm(
        desc='Fetching post stats',
        dynamic_ncols=True,
        unit=' posts',
        total=namespace.total
    )

    for line in enricher:
        post_url = line[enricher.pos]
        loading_bar.update()

        if not post_url or not is_facebook_post_url(post_url):
            enricher.write_empty(line)
            continue

        err, data = fetch_facebook_page_stats(post_url)

        if err:
            enricher.write(line, format_err(err))
        else:
            enricher.write(line, format(data))

        # Throttling
        time.sleep(FACEBOOK_DEFAULT_THROTTLE)
