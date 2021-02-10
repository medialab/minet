# =============================================================================
# Minet Facebook Comments Scraping Functions
# =============================================================================
#
# Functions able to scrape comments from Facebook posts.
#
import re
import dateparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ural import force_protocol
from ural.facebook import (
    parse_facebook_url,
    convert_facebook_url_to_mobile
)

from minet.utils import create_pool, request, rate_limited_from_state
from minet.facebook.utils import grab_facebook_cookie
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


def scrape_members_link(html):
    soup = BeautifulSoup(html, 'lxml')

    link = soup.select_one('a[href*="?view=members"]')

    if link is None:
        return None

    group_id = link.get('href').split('?', 1)[0].split('/')[-1]

    return (
        'https://m.facebook.com/browse/group/members/'
        '?id=%s&start=0&listType=list_nonfriend_nonadmin'
        % group_id
    )


def scrape_members(html):
    soup = BeautifulSoup(html, 'lxml')

    member_roots = soup.select('table[id^="member_"]')
    members = []

    for m_root in member_roots:
        title = m_root.select_one('h3 > a')
        user = parse_facebook_url(resolve_relative_url(title.get('href')))

        titles = m_root.select('h3')

        admin = False
        joined = None
        parsed_joined = None

        if len(titles) > 1:
            second_title = titles[1]

            if 'Admin' in second_title.get_text():
                admin = True

            joined = second_title.select_one('abbr').get_text().strip()
            parsed_joined = parse_formatted_date(joined)

        member = {
            'user_id': getattr(user, 'id', ''),
            'user_handle': getattr(user, 'handle', ''),
            'user_url': getattr(user, 'url', ''),
            'user_label': title.get_text().strip(),
            'admin': admin,
            'formatted_joined': joined,
            'joined': parsed_joined.isoformat() if parsed_joined else ''
        }

        members.append(member)

    next_link = soup.select_one('a[href^="/browse/group/members/?"]')
    next_link = resolve_relative_url(next_link.get('href')) if next_link else None

    return next_link, members


class FacebookMemberScraper(object):
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

        html = self.request_page(url)

        members_link = scrape_members_link(html)

        while members_link is not None:
            html = self.request_page(members_link)

            next_link, members = scrape_members(html)

            yield from members

            members_link = next_link
