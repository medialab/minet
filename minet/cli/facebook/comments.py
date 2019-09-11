# =============================================================================
# Minet Facebook Comments CLI Action
# =============================================================================
#
# Logic of the `fb comments` action.
#
import re
import csv
import sys
import time
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin
from http.cookies import SimpleCookie
from tqdm import tqdm

from minet.utils import grab_cookies, create_safe_pool, fetch
from minet.cli.utils import DummyTqdmFile

DEFAULT_THROTTLE = 0.5
BASE_URL = 'https://m.facebook.com'
VALID_ID_RE = re.compile(r'^(?:see_next_)?\d+$')

CSV_HEADERS = [
    'post_id',
    'comment_id',
    'user_name',
    'user_url',
    'comment_text',
    'formatted_date',
    'reactions',
    'replies',
    'in_reply_to'
]


def fix_cookie(cookie_string):
    cookie = SimpleCookie()
    cookie.load(cookie_string)

    # NOTE: those cookie items can rat you out
    try:
        del cookie['m_pixel_ratio']
        del cookie['wd']
    except KeyError:
        pass

    cookie['locale'] = 'en_US'

    return '; '.join(key + '=' + morsel.coded_value for key, morsel in cookie.items())


def format_csv_row(comments):
    row = []

    for key in CSV_HEADERS:
        row.append(comments[key] or '')

    return row


def scrape_comments(html, in_reply_to=None):
    soup = BeautifulSoup(html, 'lxml')

    data = {
        'post_id': None,
        'comments': [],
        'next': None,
        'replies': [],
        'in_reply_to': in_reply_to
    }

    valid_items = (
        item
        for item
        in soup.select('[id]')
        if VALID_ID_RE.match(item.get('id'))
    )

    for item in valid_items:
        item_id = item.get('id')

        if item_id is None:
            continue

        if item_id.startswith('see_next'):
            next_link = item.select_one('a')
            data['next'] = urljoin(BASE_URL, next_link.get('href'))
            break

        # Skipping comment if same as commented
        if item_id == in_reply_to:
            continue

        user_link = item.select_one('h3 > a')
        user_name = user_link.get_text().strip()

        # TODO: link to comment

        # TODO: clean it!
        user_url = user_link.get('href')

        # TODO: maybe get html instead
        comment_text = item.select_one('h3 + div').get_text().strip()
        formatted_date = item.select_one('abbr').get_text().strip()

        post_id = item.select_one('[id^="like_"]').get('id').split('_')[1]

        # TODO: this is baaaad
        data['post_id'] = post_id

        reactions_item = item.select_one('[aria-label*=" reaction"]')
        reactions = '0'

        if reactions_item is not None:
            reactions = reactions_item.get_text().strip()

        replies_items = item.select('a[href^="/comment/replies"]')
        replies = '0'

        if len(replies_items) > 0:
            replies_item = replies_items[-1]

            if replies_item is not None:
                replies_text = replies_item.get_text()

                if replies_text != 'Reply':
                    replies = replies_text.split('·')[-1].split(' replie')[0].strip()

                    replies_url = replies_item.get('href')
                    data['replies'].append((urljoin(BASE_URL, replies_url), item_id))

        data['comments'].append({
            'post_id': post_id,
            'comment_id': item_id,
            'user_name': user_name,
            'user_url': user_url,
            'comment_text': comment_text,
            'formatted_date': formatted_date,
            'reactions': reactions,
            'replies': replies,
            'in_reply_to': in_reply_to
        })

    return data


def facebook_comments_action(namespace):

    # Handling output
    if namespace.output is None:
        output_file = DummyTqdmFile(sys.stdout)
    else:
        output_file = open(namespace.output, 'w')

    writer = csv.writer(output_file)
    writer.writerow(CSV_HEADERS)

    # Loading bar
    loading_bar = tqdm(
        desc='Scraping comments',
        dynamic_ncols=True,
        unit=' comments'
    )

    # Reformatting url to hit mobile website
    # TODO: support ids & better heuristics for m. implementation
    # TODO: beware of locale
    url = namespace.url.replace('www', 'm')

    # Grabbing cookies
    get_cookie_for_url = grab_cookies()
    cookie = fix_cookie(get_cookie_for_url(url))

    http = create_safe_pool()

    def fetch_page(target):
        error, result = fetch(http, target, cookie=cookie)

        if error is not None:
            raise error

        return result.data.decode('utf-8')

    url_queue = deque([(url, None)])

    url_count = 0
    replies_count = 0

    while len(url_queue) != 0:
        current_url, in_reply_to = url_queue.popleft()

        html = fetch_page(current_url)
        data = scrape_comments(html, in_reply_to)

        url_count += 1

        for reply_url, commented_id in data['replies']:
            url_queue.append((reply_url, commented_id))

        if data['next'] is not None:
            url_queue.append((data['next'], in_reply_to))

        for comment in data['comments']:
            loading_bar.update()
            writer.writerow(format_csv_row(comment))

            if in_reply_to is not None:
                replies_count += 1

        loading_bar.set_postfix(urls=url_count, replies=replies_count)

        # Don't be too greedy
        time.sleep(DEFAULT_THROTTLE)
