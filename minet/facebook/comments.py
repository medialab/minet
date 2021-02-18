# =============================================================================
# Minet Facebook Comments Scraping Functions
# =============================================================================
#
# Functions able to scrape comments from Facebook posts.
#
import re
import sys
import dateparser
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin
from ural import force_protocol
from ural.facebook import (
    parse_facebook_url,
    convert_facebook_url_to_mobile
)

from minet.utils import create_pool, request, rate_limited_from_state
from minet.facebook.utils import grab_facebook_cookie
from minet.facebook.formatters import format_comment
from minet.facebook.exceptions import FacebookInvalidCookieError
from minet.facebook.constants import (
    FACEBOOK_OUTPUT_FORMATS,
    FACEBOOK_MOBILE_RATE_LIMITER_STATE,
    FACEBOOK_MOBILE_URL
)

VALID_ID_RE = re.compile(r'^\d+$')


def parse_formatted_date(formatted_date):
    try:
        return dateparser.parse(
            formatted_date,
            languages=['en']
        )
    except ValueError:
        return None


def resolve_relative_url(url):
    return urljoin(FACEBOOK_MOBILE_URL, url)


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

    # Detecting if we are in a video pagelet
    video_pagelet = soup.select_one('#mobile_injected_video_feed_pagelet')

    if video_pagelet is not None:
        actual_comments_link = video_pagelet.select_one('a[href^="/story.php?"]')

        if actual_comments_link:
            data['next'] = resolve_relative_url(actual_comments_link.get('href'))

        return data

    if not in_reply_to:
        if direction is None or direction == 'forward':
            next_link = soup.select_one('[id^="see_next_"] > a[href]')

            if next_link:
                data['next'] = resolve_relative_url(next_link.get('href'))

                if direction is None:
                    data['direction'] = 'forward'

        if direction is None or direction == 'backward':
            next_link = soup.select_one('[id^="see_prev_"] > a[href]')

            if next_link:
                data['next'] = resolve_relative_url(next_link.get('href'))

                if direction is None:
                    data['direction'] = 'backward'
    else:
        if direction is None or direction == 'backward':
            next_link = soup.select_one('[id^="comment_replies_more_1"] > a[href]')

            if next_link:
                data['next'] = resolve_relative_url(next_link.get('href'))

                if direction is None:
                    data['direction'] = 'backward'

    valid_items = (
        item
        for item
        in soup.select('[id]')
        if VALID_ID_RE.match(item.get('id'))
        and not item.parent.get('id', '').startswith('comment_replies_more')
    )

    for item in valid_items:
        item_id = item.get('id')

        # Skipping comment if same as commented
        if item_id == in_reply_to:
            continue

        user_link = item.select_one('h3 > a')

        # NOTE: this is a raise bomb
        if not user_link:
            raise TypeError

        user_label = user_link.get_text().strip()
        user_href = user_link.get('href')
        user = parse_facebook_url(resolve_relative_url(user_href))

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

        comment_text = '\n'.join(el.get_text().strip() for el in content_elements)
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

                    if 'See all' in replies_text:
                        replies = replies_text.split('See all')[-1].split(' replies')[0].strip()
                    else:
                        replies = replies_text.split('·')[-1].split(' repl')[0].strip()

                    replies_url = replies_item.get('href')
                    data['replies'].append((resolve_relative_url(replies_url), item_id))

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


class FacebookCommentScraper(object):
    def __init__(self, cookie):

        # Grabbing cookie
        cookie = grab_facebook_cookie(cookie)

        if cookie is None:
            raise FacebookInvalidCookieError

        self.cookie = cookie
        self.http = create_pool()

    @rate_limited_from_state(FACEBOOK_MOBILE_RATE_LIMITER_STATE)
    def request_page(self, url):
        error, result = request(
            self.http,
            url,
            cookie=self.cookie,
            headers={
                'User-Agent': 'curl/7.68.0'
            }
        )

        if error is not None:
            raise error

        return result.data.decode('utf-8')

    def __call__(self, url, detailed=False, per_call=False, format='raw'):

        if format not in FACEBOOK_OUTPUT_FORMATS:
            raise TypeError('minet.facebook.scrape_comments: unkown `format`.')

        # Reformatting url to hit mobile website
        url = force_protocol(url, 'https')
        url = convert_facebook_url_to_mobile(url)

        url_queue = deque([(url, None, None)])

        calls = 0
        replies = 0

        while len(url_queue) != 0:
            current_url, direction, in_reply_to = url_queue.popleft()

            html = self.request_page(current_url)

            try:
                data = scrape_comments(html, direction, in_reply_to)
            except TypeError:
                # with open('./dump.html', 'w') as f:
                #     f.write(html)
                print('Could not process comment in %s' % current_url, file=sys.stderr)
                sys.exit(1)

            calls += 1

            for reply_url, commented_id in data['replies']:
                url_queue.append((reply_url, None, commented_id))

            if data['next'] is not None:
                url_queue.append((data['next'], data['direction'], in_reply_to))

            comments = []

            for comment in data['comments']:
                if in_reply_to is not None:
                    replies += 1

                if format == 'csv_row':
                    comment = format_comment(comment)

                if per_call:
                    comments.append(comment)
                else:
                    yield comment

            if per_call and len(comments) > 0:
                if detailed:
                    details = {
                        'calls': calls,
                        'replies': replies,
                        'queue_size': len(url_queue)
                    }

                    yield details, comments
                else:
                    yield comments
