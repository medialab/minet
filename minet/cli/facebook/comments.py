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
import urllib3
import certifi
from bs4 import BeautifulSoup
from pycookiecheat import chrome_cookies
from collections import deque
from urllib.parse import urljoin
from tqdm import tqdm

from minet.cli.utils import DummyTqdmFile, print_err

# TODO: centralize this for god's sake
SPOOFED_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:69.0) Gecko/20100101 Firefox/69.0'
BASE_URL = 'https://m.facebook.com'
THROTTLE = 0.5

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

    # Grabbing cookies from local Chrome
    cookies = chrome_cookies(url)
    del cookies['m_pixel_ratio']
    del cookies['wd']

    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where(),
    )

    # TODO: abstract cookie string logic
    headers = {
        'User-Agent': SPOOFED_UA,
        'Cookie': '; '.join('%s=%s' % r for r in cookies.items())
    }

    def fetch(target):
        result = http.request('GET', target, headers=headers)
        return result.data.decode('utf-8')

    url_queue = deque([(url, None)])

    url_count = 0
    replies_count = 0

    while len(url_queue) != 0:
        current_url, in_reply_to = url_queue.popleft()

        html = fetch(current_url)
        data = scrape_comments(html, in_reply_to)

        url_count += 1

        for reply_url, commented_id in data['replies']:
            url_queue.append((reply_url, commented_id))

        if data['next'] is not None:
            url_queue.append(data['next'])

        for comment in data['comments']:
            loading_bar.update()
            writer.writerow(format_csv_row(comment))

            if in_reply_to is not None:
                replies_count += 1

        loading_bar.set_postfix(urls=url_count, replies=replies_count)

        time.sleep(THROTTLE)
