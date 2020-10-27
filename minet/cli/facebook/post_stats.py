# =============================================================================
# Minet Facebook Post Stats CLI Action
# =============================================================================
#
# Logic of the `fb post-stats` action.
#
import re
import json5
import casanova
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime
from collections import OrderedDict
from ural.facebook import is_facebook_url

from minet.utils import create_pool, request, nested_get, sleep_with_entropy
from minet.cli.utils import open_output_file, print_err, die
from minet.cli.facebook.constants import FACEBOOK_WEB_DEFAULT_THROTTLE

META_EXTRACTOR_TEMPLATE = rb'\(function\(\)\{bigPipe\.onPageletArrive\((\{.+share_fbid:"%s".+\})\);\}\),"onPageletArrive'
HTML_EXTRACTOR_TEMPLATE = rb'<code[^>]*><!--(.+%s.+)--></code>'
CURRENT_AVAILABILITY_DISCLAIMER = b'The link you followed may have expired, or the page may only be visible to an audience'
AVAILABILITY_DISCLAIMER = b'The link you followed may be broken, or the page may have been removed'
LOGIN_DISCLAIMER = b'You must log in to continue'
CAPTCHA = b'id="captcha"'

REPORT_HEADERS = [
    'error',
    'canonical',
    'account_name',
    'timestamp',
    'time',
    'link',
    'aria_label',
    'text',
    'share_count',
    'comment_count',
    'reaction_count',
    'video_view_count'
]

REACTION_KEYS = OrderedDict({
    1: 'like',
    2: 'love',
    3: 'wow',
    4: 'haha',
    7: 'sad',
    8: 'angry',
    11: 'thankful',
    12: 'pride'
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
            print_err('Found unkown emotion %s' % edge)
            continue

        index[emotion] = edge['reaction_count'] or 0

    return index


def format_err(err):
    return [err] + ERROR_PADDING


def format(data):
    video_view_count = data.get('video_view_count')
    scraped = data['scraped'] or {}

    row = [
        '',
        data.get('url', ''),
        scraped.get('account_name', ''),
        scraped.get('timestamp', ''),
        scraped.get('time', ''),
        scraped.get('link', ''),
        scraped.get('aria_label', ''),
        scraped.get('text', ''),
        get_count(data['share_count']),
        get_count(data['comment_count']),
        get_count(data['reaction_count']),
        video_view_count if isinstance(video_view_count, int) else ''
    ]

    emotion_index = collect_top_reactions(data)

    for emotion_name in REACTION_KEYS.values():
        row.append(emotion_index.get(emotion_name, 0))

    return row


def facebook_post_stats_action(namespace):

    # Handling output
    output_file = open_output_file(namespace.output)

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        add=REPORT_HEADERS,
        keep=namespace.select
    )

    http = create_pool()

    def fetch_facebook_page_stats(url):
        err, response = request(http, url, cookie='locale=en_US')

        if err:
            return 'http-error', None

        if response.status == 404:
            return 'not-found', None

        if response.status >= 400:
            return 'http-error', None

        html = response.data

        if CAPTCHA in html:
            die([
                'Rate limit reached!',
                'Last url: %s' % url
            ])

        if (
            CURRENT_AVAILABILITY_DISCLAIMER in html or
            AVAILABILITY_DISCLAIMER in html
        ):
            return 'unavailable', None

        if LOGIN_DISCLAIMER in html:
            return 'private-or-unavailable', None

        # TODO: integrate into ural
        bpost_id = url.rsplit('/', 1)[-1].encode()

        # Extracting metadata
        meta_extractor = re.compile(META_EXTRACTOR_TEMPLATE % bpost_id)

        match = meta_extractor.search(html)

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

        if 'political_figure_data' in data and data['political_figure_data']:
            print_err('Found political_figure_data:')
            print_err(data['political_figure_data'])

        if get_count(data['reaction_count']) != get_count(data['reactors']):
            print_err('Found different reactions/reactors for %s' % url)

        # Extracting data from hidden html
        hidden_html_extractor = re.compile(HTML_EXTRACTOR_TEMPLATE % bpost_id)
        match = hidden_html_extractor.search(html)

        if match is not None:
            hidden_html = match.group(1).decode()
            soup = BeautifulSoup(hidden_html, 'lxml')

            # Sometimes fetching a post behaves weirdly
            if soup.select_one('h5 a') is None:
                return 'extraction-failed', None

            data['scraped'] = {}

            timestamp_elem = soup.select_one('[data-utime]')
            timestamp = int(timestamp_elem.get('data-utime'))

            data['scraped']['account_name'] = soup.select_one('h5 a').get_text().strip()
            data['scraped']['timestamp'] = timestamp
            data['scraped']['time'] = datetime.fromtimestamp(timestamp).isoformat()

            # TODO: use a context manager
            try:
                data['scraped']['aria_label'] = timestamp_elem.parent.get('aria-label')
            except:
                pass

            try:
                data['scraped']['text'] = soup.select_one('[data-testid="post_message"]').get_text()
            except:
                pass

            # try:
            #     data['scraped']['link'] = soup.select_one('[data-lynx-uri]').get('href')
            # except:
            #     pass

        return None, data

    # Loading bar
    loading_bar = tqdm(
        desc='Fetching post stats',
        dynamic_ncols=True,
        unit=' posts',
        total=namespace.total
    )

    for row, post_url in enricher.cells(namespace.column, with_rows=True):
        loading_bar.update()

        if (
            not post_url or
            not is_facebook_post_url(post_url) or
            not is_facebook_url(post_url)
        ):
            enricher.writerow(row, format_err('not-facebook-post'))
            continue

        err, data = fetch_facebook_page_stats(post_url)

        if err:
            enricher.writerow(row, format_err(err))
        else:
            enricher.writerow(row, format(data))

        # Throttling
        sleep_with_entropy(FACEBOOK_WEB_DEFAULT_THROTTLE, 5.0)
