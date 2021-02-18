# =============================================================================
# Minet Facebook Post Id From Url
# =============================================================================
#
# Helper used to retrieved a full facebook post id from the given post url.
#
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, parse_qsl, urljoin
from ural.facebook import (
    convert_facebook_url_to_mobile,
    parse_facebook_url,
    FacebookPost
)

from minet.utils import rate_limited_from_state, request_text
from minet.facebook.constants import (
    FACEBOOK_URL,
    FACEBOOK_MOBILE_URL,
    FACEBOOK_MOBILE_RATE_LIMITER_STATE,
    FACEBOOK_DEFAULT_POOL
)

PAGE_ID_PATTERN = re.compile(r'&amp;rid=(\d+)&amp;')
GROUP_ID_PATTERN = re.compile(r'fb://group/(\d+)')


@rate_limited_from_state(FACEBOOK_MOBILE_RATE_LIMITER_STATE)
def page_id_from_handle(handle):
    url = urljoin(FACEBOOK_MOBILE_URL, handle)

    err, response, html = request_text(FACEBOOK_DEFAULT_POOL, url, headers={
        'User-Agent': 'curl/7.68.0'
    })

    if err:
        raise err

    if response.status >= 400:
        return None

    m = PAGE_ID_PATTERN.search(html)

    if m is None:
        return None

    return m.group(1)


@rate_limited_from_state(FACEBOOK_MOBILE_RATE_LIMITER_STATE)
def group_id_from_handle(handle):
    url = urljoin(FACEBOOK_MOBILE_URL, 'groups/%s' % handle)

    err, response, html = request_text(FACEBOOK_DEFAULT_POOL, url, headers={
        'User-Agent': 'curl/7.68.0'
    })

    if err:
        raise err

    if response.status >= 400:
        return None

    m = GROUP_ID_PATTERN.search(html)

    if m is None:
        return None

    return m.group(1)


@rate_limited_from_state(FACEBOOK_MOBILE_RATE_LIMITER_STATE)
def scrape_post_id(post_url):
    post_mobile_url = convert_facebook_url_to_mobile(post_url)

    err, response, html = request_text(FACEBOOK_DEFAULT_POOL, post_mobile_url)

    if err:
        raise err

    soup = BeautifulSoup(html, 'lxml')

    root_element = soup.select_one('#m_story_permalink_view [data-ft]')

    if root_element is None:

        # Is this a photo post?
        next_link = soup.select_one('[href^="/photo.php"]')

        if next_link is None:
            return

        href = next_link.get('href')

        if not href:
            return

        link = urljoin(FACEBOOK_URL, href)
        query = urlsplit(link).query

        if not query:
            return

        query = dict(parse_qsl(query))

        return '%s_%s' % (query['id'], query['fbid'])

    data = root_element.get('data-ft')

    if data is None:
        return

    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        return

    content_owner_id_new = data.get('content_owner_id_new') or data.get('page_id')
    mf_story_key = data.get('mf_story_key')

    if content_owner_id_new is None or mf_story_key is None:
        return

    return '%s_%s' % (content_owner_id_new, mf_story_key)


# TODO: could easily cache some retrieved handles...
def post_id_from_url(post_url):
    parsed = parse_facebook_url(post_url)

    if not isinstance(parsed, FacebookPost):
        return

    if parsed.full_id is not None:
        return parsed.full_id

    if parsed.parent_handle is not None:
        parent_id = page_id_from_handle(parsed.parent_handle)

        if parent_id is not None:
            return '%s_%s' % (parent_id, parsed.id)

    elif parsed.group_handle is not None:
        group_id = group_id_from_handle(parsed.group_handle)

        if group_id is not None:
            return '%s_%s' % (group_id, parsed.id)

    return scrape_post_id(post_url)
