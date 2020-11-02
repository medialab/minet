# =============================================================================
# Minet Facebook Comments CLI Action
# =============================================================================
#
# Logic of the `fb comments` action.
#
import re
import csv
import time
import dateparser
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin
from tqdm import tqdm
from ural import force_protocol
from ural.facebook import (
    parse_facebook_url,
    convert_facebook_url_to_mobile
)

from minet.utils import create_pool, request
from minet.cli.utils import open_output_file
from minet.cli.facebook.utils import grab_facebook_cookie
from minet.cli.facebook.constants import FACEBOOK_MOBILE_DEFAULT_THROTTLE

BASE_URL = 'https://m.facebook.com'
VALID_ID_RE = re.compile(r'^\d+$')

CSV_HEADERS = [
    'post_id',
    'comment_id',
    'user_id',
    'user_handle',
    'user_url',
    'user_label',
    'comment_text',
    'comment_html',
    'formatted_date',
    'date',
    'reactions',
    'replies',
    'in_reply_to'
]


def format_csv_row(comments):
    row = []

    for key in CSV_HEADERS:
        row.append(comments[key] or '')

    return row


def parse_formatted_date(formatted_date):
    try:
        return dateparser.parse(
            formatted_date,
            languages=['en']
        )
    except ValueError:
        return None


def scrape_comments(html, direction=None, in_reply_to=None):
    soup = BeautifulSoup(html, 'lxml')

    data = {
        'direction': direction,
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

    if not in_reply_to:
        if direction is None or direction == 'forward':
            next_link = soup.select_one('[id^="see_next_"] > a[href]')

            if next_link:
                data['next'] = urljoin(BASE_URL, next_link.get('href'))

                if direction is None:
                    data['direction'] = 'forward'

        if direction is None or direction == 'backward':
            next_link = soup.select_one('[id^="see_prev_"] > a[href]')

            if next_link:
                data['next'] = urljoin(BASE_URL, next_link.get('href'))

                if direction is None:
                    data['direction'] = 'backward'
    else:
        if direction is None or direction == 'backward':
            next_link = soup.select_one('[id^="comment_replies_more_1"] > a[href]')

            if next_link:
                data['next'] = urljoin(BASE_URL, next_link.get('href'))

                if direction is None:
                    data['direction'] = 'backward'

    for item in valid_items:
        item_id = item.get('id')

        # Skipping comment if same as commented
        if item_id == in_reply_to:
            continue

        user_link = item.select_one('h3 > a')

        # TODO: this should be fixed. Truncated comments are not correctly handled
        if not user_link:
            raise TypeError

        user_label = user_link.get_text().strip()
        user_href = user_link.get('href')
        user = parse_facebook_url(urljoin(BASE_URL, user_href))

        # TODO: link to comment
        content_elements_candidates = item.select_one('h3').find_next_siblings('div')
        content_elements = []
        content_elements_html = []

        for el in content_elements_candidates:
            if el.select_one('[id^=like_]'):
                break

            content_elements_html.append(el)

            if el.get_text().strip():
                content_elements.append(el)

        comment_text = '\n\n'.join(el.get_text().strip() for el in content_elements)
        comment_html = ''.join(str(el) for el in content_elements_html)

        formatted_date = item.select_one('abbr').get_text().strip()
        parsed_date = parse_formatted_date(formatted_date)

        post_id = item.select_one('[id^="like_"]').get('id').split('_')[1]

        # NOTE: this could be better (we already know this beforehand)
        data['post_id'] = post_id

        reactions_item = item.select_one('[href^="/ufi/reaction/"]')
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
                    replies = replies_text.split('·')[-1].split(' repl')[0].strip()

                    replies_url = replies_item.get('href')
                    data['replies'].append((urljoin(BASE_URL, replies_url), item_id))

        data['comments'].append({
            'post_id': post_id,
            'comment_id': item_id,
            'user_id': getattr(user, 'id', ''),
            'user_handle': getattr(user, 'handle', ''),
            'user_url': getattr(user, 'url', ''),
            'user_label': user_label,
            'comment_text': comment_text,
            'comment_html': comment_html,
            'formatted_date': formatted_date,
            'date': parsed_date.isoformat() if parsed_date else '',
            'reactions': reactions,
            'replies': replies,
            'in_reply_to': in_reply_to
        })

    return data


def facebook_comments_action(namespace):

    # Reformatting url to hit mobile website
    url = force_protocol(namespace.url, 'https')
    url = convert_facebook_url_to_mobile(url)

    # Grabbing cookie
    cookie = grab_facebook_cookie(namespace)

    # Handling output
    output_file = open_output_file(namespace.output)

    writer = csv.writer(output_file)
    writer.writerow(CSV_HEADERS)

    http = create_pool()

    def request_page(target):
        error, result = request(
            http,
            target,
            cookie=cookie,
            headers={
                'User-Agent': 'curl/7.68.0'
            }
        )

        if error is not None:
            raise error

        return result.data.decode('utf-8')

    # Loading bar
    loading_bar = tqdm(
        desc='Scraping comments',
        dynamic_ncols=True,
        unit=' comments'
    )

    url_queue = deque([(url, None, None)])

    url_count = 0
    replies_count = 0

    while len(url_queue) != 0:
        current_url, direction, in_reply_to = url_queue.popleft()

        html = request_page(current_url)

        try:
            data = scrape_comments(html, direction, in_reply_to)
        except TypeError:
            from minet.cli.utils import die
            die(['stop', current_url])

        # with open('page.html', 'w') as of:
        #     of.write(html)

        # from pprint import pprint
        # pprint(data)

        # from minet.cli.utils import die
        # die('stop debug')

        url_count += 1

        for reply_url, commented_id in data['replies']:
            url_queue.append((reply_url, None, commented_id))

        if data['next'] is not None:
            url_queue.append((data['next'], data['direction'], in_reply_to))

        for comment in data['comments']:
            loading_bar.update()
            writer.writerow(format_csv_row(comment))

            if in_reply_to is not None:
                replies_count += 1

        loading_bar.set_postfix(
            urls=url_count,
            replies=replies_count,
            q=len(url_queue)
        )

        # Don't be too greedy
        time.sleep(FACEBOOK_MOBILE_DEFAULT_THROTTLE)

    loading_bar.close()
