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
from collections import OrderedDict
from ural.facebook import is_facebook_url

from minet.utils import create_pool, request, nested_get
from minet.cli.utils import open_output_file, CSVEnricher, print_err
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
    'reaction_count'
]

REACTION_KEYS = OrderedDict({
    1: 'like',
    2: 'love',
    3: 'wow',
    4: 'haha',
    7: 'sad',
    8: 'angry'
})

for emotion_name in REACTION_KEYS.values():
    REPORT_HEADERS.append('%s_count' % emotion_name)

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


def collect_top_reactions(data):
    edges = nested_get(['top_reactions', 'edges'], data)

    if edges is None:
        return

    index = {}

    for edge in edges:
        emotion = REACTION_KEYS.get(edge['node']['key'])

        if emotion is None:
            raise TypeError('Found unkown emotion %s' % edge)

        index[emotion] = edge['reaction_count'] or 0

    return index


def format_err(err):
    return [err] + ERROR_PADDING


def format(data):
    row = [
        '',
        get_count(data['share_count']),
        get_count(data['comment_count']),
        get_count(data['reaction_count'])
    ]

    emotion_index = collect_top_reactions(data)

    for emotion_name in REACTION_KEYS.values():
        row.append(emotion_index.get(emotion_name, 0))

    return row


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

        # TODO: remove, this is here as a test
        # TODO: try to find a post where comments are disabled
        if get_count(data['seen_by_count']):
            print_err('Found seen_by_count: %i for %s' % (get_count(data['seen_by_count']), url))

        if get_count(data['video_view_count']):
            print_err('Found video_view_count: %i for %s' % (get_count(data['video_view_count']), url))

        if 'political_figure_data' in data and data['political_figure_data']:
            print_err('Found political_figure_data: %i for %s' % (data['political_figure_data'], url))

        if get_count(data['reaction_count']) != get_count(data['reactors']):
            print_err('Found different reactions/reactors for %s' % url)

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

        if (
            not post_url or
            not is_facebook_post_url(post_url) or
            not is_facebook_url(post_url)
        ):
            enricher.write(line, format_err('not-facebook-post'))
            continue

        err, data = fetch_facebook_page_stats(post_url)

        if err:
            enricher.write(line, format_err(err))
        else:
            enricher.write(line, format(data))

        # Throttling
        time.sleep(FACEBOOK_DEFAULT_THROTTLE)
