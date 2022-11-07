# =============================================================================
# Minet Facebook Comments Scraping Functions
# =============================================================================
#
# Functions able to scrape comments from Facebook posts.
#
import re
import sys
import soupsieve
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin
from ural import force_protocol
from ural.facebook import (
    parse_facebook_url,
    convert_facebook_url_to_mobile,
    has_facebook_comments,
    FacebookGroup as ParsedFacebookGroup,
    FacebookHandle as ParsedFacebookHandle,
    FacebookUser as ParsedFacebookUser,
    FacebookPost as ParsedFacebookPost,
    FacebookVideo as ParsedFacebookVideo,
    FacebookPhoto as ParsedFacebookPhoto,
)

from minet.utils import (
    rate_limited_method,
    RateLimiterState,
    parse_date,
    clean_human_readable_numbers,
)
from minet.web import create_pool, request, create_request_retryer, retrying_method
from minet.scrape.std import get_display_text
from minet.facebook.utils import grab_facebook_cookie
from minet.facebook.formatters import (
    FacebookComment,
    FacebookPost,
    FacebookUser,
    FacebookPostWithReaction,
)
from minet.facebook.exceptions import (
    FacebookInvalidCookieError,
    FacebookInvalidTargetError,
    FacebookNotPostError,
    FacebookWatchError,
)
from minet.facebook.constants import (
    FACEBOOK_MOBILE_DEFAULT_THROTTLE,
    FACEBOOK_MOBILE_URL,
)

VALID_ID_RE = re.compile(r"^\d+$")


def convert_url_to_mobile(url):
    url = force_protocol(url, "https")
    return convert_facebook_url_to_mobile(url)


def cleanup_post_link(url):
    url = url.replace("//m.", "//www.")

    return url.split("?", 1)[0]


def extract_user_information_from_link(element):
    user_label = element.get_text().strip()
    user_href = element.get("href")
    user = parse_facebook_url(resolve_relative_url(user_href))

    return user_label, user


def resolve_relative_url(url):
    return urljoin(FACEBOOK_MOBILE_URL, url)


def scrape_comments(html, direction=None, in_reply_to=None):
    soup = BeautifulSoup(html, "lxml")

    data = {
        "direction": direction,
        "post_id": None,
        "comments": [],
        "next": None,
        "replies": [],
        "in_reply_to": in_reply_to,
    }

    # Detecting if we are in a video pagelet
    video_pagelet = soup.select_one("#mobile_injected_video_feed_pagelet")

    if video_pagelet is not None:
        actual_comments_link = video_pagelet.select_one('a[href^="/story.php?"]')

        if actual_comments_link:
            data["next"] = resolve_relative_url(actual_comments_link.get("href"))

        return data

    if not in_reply_to:
        if direction is None or direction == "forward":
            next_link = soup.select_one('[id^="see_next_"] > a[href]')

            if next_link:
                data["next"] = resolve_relative_url(next_link.get("href"))

                if direction is None:
                    data["direction"] = "forward"

        if direction is None or direction == "backward":
            next_link = soup.select_one('[id^="see_prev_"] > a[href]')

            if next_link:
                data["next"] = resolve_relative_url(next_link.get("href"))

                if direction is None:
                    data["direction"] = "backward"
    else:
        if direction is None or direction == "backward":
            next_link = soup.select_one('[id^="comment_replies_more_1"] > a[href]')

            if next_link:
                data["next"] = resolve_relative_url(next_link.get("href"))

                if direction is None:
                    data["direction"] = "backward"

    valid_items = (
        item
        for item in soup.select("[id]:has(h3 > a)")
        if VALID_ID_RE.match(item.get("id"))
        and not item.parent.get("id", "").startswith("comment_replies_more")
    )

    for item in valid_items:
        item_id = item.get("id")

        # Skipping comment if same as commented
        if item_id == in_reply_to:
            continue

        user_label, user = extract_user_information_from_link(item.select_one("h3 > a"))

        # TODO: link to comment
        content_elements_candidates = item.select_one("h3").find_next_siblings("div")
        content_elements = []
        content_elements_html = []

        for el in content_elements_candidates:
            if el.select_one("[id^=like_]"):
                break

            content_elements_html.append(el)

            if el.get_text().strip():
                content_elements.append(el)

        comment_text = get_display_text(content_elements)
        comment_html = "".join(str(el) for el in content_elements_html)

        formatted_date = item.select_one("abbr").get_text().strip()
        parsed_date = parse_date(formatted_date)

        post_id_item = item.select_one('[id^="like_"]')

        if post_id_item is None:
            raise TypeError

        post_id = item.select_one('[id^="like_"]').get("id").split("_")[1]

        # NOTE: this could be better (we already know this beforehand)
        data["post_id"] = post_id

        reactions_item = item.select_one('[href^="/ufi/reaction/"]')
        reactions = "0"

        if reactions_item is not None:
            reactions = reactions_item.get_text().strip()

        replies_items = item.select('a[href^="/comment/replies"]')
        replies = "0"

        if len(replies_items) > 0:
            replies_item = replies_items[-1]

            if replies_item is not None:
                replies_text = replies_item.get_text()

                if replies_text != "Reply":

                    if "See all" in replies_text:
                        replies = (
                            replies_text.split("See all")[-1]
                            .split(" replies")[0]
                            .strip()
                        )
                    else:
                        replies = replies_text.split("·")[-1].split(" repl")[0].strip()

                    replies_url = replies_item.get("href")
                    data["replies"].append((resolve_relative_url(replies_url), item_id))

        data["comments"].append(
            FacebookComment(
                post_id=post_id,
                id=item_id,
                user_id=getattr(user, "id", ""),
                user_handle=getattr(user, "handle", ""),
                user_url=getattr(user, "url", ""),
                user_label=user_label,
                text=comment_text,
                html=comment_html,
                formatted_date=formatted_date,
                date=parsed_date,
                reactions=reactions,
                replies=replies,
                in_reply_to=in_reply_to,
            )
        )

    return data


def scrape_posts(html):
    soup = BeautifulSoup(html, "lxml")

    next_link = soup.select_one('a[href*="?bacr="], a[href*="&bacr="]')

    if next_link is not None:
        next_link = resolve_relative_url(next_link.get("href"))

    posts = []
    post_elements = soup.select("#m_group_stories_container > div > [data-ft]")

    for el in post_elements:
        full_story_link = soupsieve.select_one('a:-soup-contains("Full Story")', el)

        if not full_story_link:
            continue

        post_url = cleanup_post_link(full_story_link.get("href"))

        user_label, user = extract_user_information_from_link(el.select_one("h3 a"))

        formatted_date = el.select_one("abbr").get_text().strip()
        parsed_date = parse_date(formatted_date)

        reactions_item = el.select_one('[id^="like_"]')
        reactions = "0"

        if reactions_item:
            reactions_text = reactions_item.get_text()

            if reactions_text.count("·") > 1:
                reactions = reactions_text.split("·", 1)[0].strip()

        comments_item = soupsieve.select_one('a:-soup-contains(" Comment")', el)
        comments = "0"

        if comments_item:
            comments = comments_item.get_text().split("Comment", 1)[0].strip()

        text_root = el.select_one('[data-ft=\'{"tn":"*s"}\']')
        additional_html_roots = []

        img_root = el.select_one('[data-ft=\'{"tn":"H"}\']')

        if img_root:
            additional_html_roots.append(img_root)

        all_text_elements = text_root.find_all("div", recursive=False)

        text_elements = []
        translated_text_elements = []
        translation_link = None

        for text_el in all_text_elements:
            translation_link = text_el.select_one(
                'a[href^="/basic/translation_preferences/"]'
            )
            if translation_link is None:
                text_elements.append(text_el)
            else:
                translation_link.extract()
                translated_text_elements.append(text_el)

        html_elements = text_elements + additional_html_roots

        comment_text = get_display_text(text_elements)
        comment_html = "".join(str(el) for el in html_elements)

        translated_comment_text = get_display_text(translated_text_elements)
        translated_comment_html = "".join(str(el) for el in translated_text_elements)
        translated_from = (
            translation_link.get_text().rsplit("from ", 1)[-1].strip()
            if translation_link
            else None
        )

        post = FacebookPost(
            url=post_url,
            user_id=getattr(user, "id", ""),
            user_handle=getattr(user, "handle", ""),
            user_url=getattr(user, "url", ""),
            user_label=user_label,
            text=comment_text,
            html=comment_html,
            translated_text=translated_comment_text,
            translated_html=translated_comment_html,
            translated_from=translated_from,
            formatted_date=formatted_date,
            date=parsed_date,
            reactions=reactions,
            comments=comments,
        )

        posts.append(post)

    return next_link, posts


def scrape_video(soup):

    video_url_html = soup.select_one("meta[property='og:video:url']")

    if not video_url_html:

        title = soup.head.select_one("title").get_text().lower()

        if title == "facebook watch":
            raise FacebookWatchError

        raise FacebookInvalidTargetError

    video_url = video_url_html.get("content")

    user_label = None
    user = None
    user_link = soup.select_one("h3 a")

    if user_link:
        user_label, user = extract_user_information_from_link(user_link)

    formatted_date = soup.select_one("abbr").get_text().strip()
    parsed_date = parse_date(formatted_date)

    reactions_item = soup.select_one('[id^="like_"]')
    reactions = "0"

    if reactions_item:
        reactions_text = reactions_item.get_text()

        if reactions_text.count("·") > 1:
            reactions = clean_human_readable_numbers(
                reactions_text.split("·", 1)[0].strip()
            )

    comments_item = soupsieve.select_one('a:-soup-contains(" Comment")', soup)
    comments = "0"

    if comments_item:
        comments = comments_item.get_text().split("Comment", 1)[0].strip()

    text_root = soup.select_one('[data-ft=\'{"tn":"*s"}\']')
    additional_html_roots = []

    img_root = soup.select_one('[data-ft=\'{"tn":"H"}\']')

    if img_root:
        additional_html_roots.append(img_root)

    all_text_elements = text_root.find_all("div", recursive=False)

    text_elements = []
    translated_text_elements = []
    translation_link = None

    for text_el in all_text_elements:
        translation_link = text_el.select_one(
            'a[href^="/basic/translation_preferences/"]'
        )
        if translation_link is None:
            text_elements.append(text_el)
        else:
            translation_link.extract()
            translated_text_elements.append(text_el)

    html_elements = text_elements + additional_html_roots

    comment_text = get_display_text(text_elements)
    comment_html = "".join(str(el) for el in html_elements)

    translated_comment_text = get_display_text(translated_text_elements)
    translated_comment_html = "".join(str(el) for el in translated_text_elements)
    translated_from = (
        translation_link.get_text().rsplit("from ", 1)[-1].strip()
        if translation_link
        else None
    )

    post = FacebookPostWithReaction(
        url=video_url,
        user_id=getattr(user, "id", ""),
        user_handle=getattr(user, "handle", ""),
        user_url=getattr(user, "url", ""),
        user_label=user_label,
        text=comment_text,
        html=comment_html,
        translated_text=translated_comment_text,
        translated_html=translated_comment_html,
        translated_from=translated_from,
        formatted_date=formatted_date,
        date=parsed_date,
        reactions=reactions,
        comments=comments,
        reactions_types=None,
    )
    return post


def scrape_photo(soup):

    photo_url_html = soup.select_one("meta[property='og:url']")

    if not photo_url_html:

        raise FacebookInvalidTargetError

    photo_url = photo_url_html.get("content")

    user_label = None
    user = None
    user_link = soup.select_one("a[class='actor-link']")

    if user_link:
        user_label, user = extract_user_information_from_link(user_link)

    formatted_date = soup.select_one("abbr").get_text().strip()
    parsed_date = parse_date(formatted_date)

    reactions_item = soup.select_one("a[href^='/ufi/reaction/profile/browser']")

    if reactions_item:
        reactions = clean_human_readable_numbers(reactions_item.get_text())
        reactions_types = []

        for reaction in reactions_item.find("div").select("img"):
            reactions_types.append(reaction["alt"])
        reactions_types = "|".join(reactions_types)

    comments = None

    text_root = soup.select_one(".msg")

    additional_html_roots = []

    img_root = soup.select_one("img[class='img']").get("src")

    if img_root:
        additional_html_roots.append(img_root)

    all_text_elements = (
        text_root.find_all("div", recursive=False) if text_root else None
    )

    text_elements = []
    translated_text_elements = []
    translation_link = None

    if all_text_elements:
        for text_el in all_text_elements:
            translation_link = text_el.select_one(
                'a[href^="/basic/translation_preferences/"]'
            )
            if translation_link is None:
                text_elements.append(text_el)
            else:
                translation_link.extract()
                translated_text_elements.append(text_el)

    html_elements = text_elements + additional_html_roots

    comment_text = get_display_text(text_elements) if text_elements else None
    comment_html = "".join(str(el) for el in html_elements)

    translated_comment_text = get_display_text(translated_text_elements)
    translated_comment_html = "".join(str(el) for el in translated_text_elements)
    translated_from = (
        translation_link.get_text().rsplit("from ", 1)[-1].strip()
        if translation_link
        else None
    )

    post = FacebookPostWithReaction(
        url=photo_url,
        user_id=getattr(user, "id", ""),
        user_handle=getattr(user, "handle", ""),
        user_url=getattr(user, "url", ""),
        user_label=user_label,
        text=comment_text,
        html=comment_html,
        translated_text=translated_comment_text,
        translated_html=translated_comment_html,
        translated_from=translated_from,
        formatted_date=formatted_date,
        date=parsed_date,
        reactions=reactions,
        comments=comments,
        reactions_types=reactions_types,
    )
    return post


def scrape_post(html):
    soup = BeautifulSoup(html, "lxml")

    # with open("./dump.html", "w") as f:
    #     f.write(html)

    if soup.find("div", id="MPhotoContent"):
        return scrape_photo(soup)

    post_url_htlm = soup.head.select_one("meta[property='og:url']")

    if not post_url_htlm:

        title = soup.head.select_one("title").get_text().lower()

        if title == "facebook watch":
            raise FacebookWatchError

        raise FacebookInvalidTargetError

    post_url = post_url_htlm.get("content") if post_url_htlm else None

    if post_url == "":
        return scrape_video(soup)

    user_label = None
    user = None
    user_link = soup.select_one("h3 a")
    if user_link:
        user_label, user = extract_user_information_from_link(user_link)

    formatted_date = soup.select_one("abbr").get_text().strip()
    parsed_date = parse_date(formatted_date)

    reactions_item = soup.select_one("a[href^='/ufi/reaction/profile/browser']")

    if reactions_item:
        reactions = clean_human_readable_numbers(reactions_item.get_text())
        reactions_types = []

        for reaction in reactions_item.find("div").select("img"):
            reactions_types.append(reaction["alt"])
        reactions_types = "|".join(reactions_types)

    comments = None

    text_root = soup.select_one('[data-ft=\'{"tn":"*s"}\']')
    additional_html_roots = []

    img_root = soup.select_one('[data-ft=\'{"tn":"H"}\']')

    if img_root:
        additional_html_roots.append(img_root)

    all_text_elements = (
        text_root.find_all("div", recursive=False) if text_root else None
    )

    text_elements = []
    translated_text_elements = []
    translation_link = None

    if all_text_elements:
        for text_el in all_text_elements:
            translation_link = text_el.select_one(
                'a[href^="/basic/translation_preferences/"]'
            )
            if translation_link is None:
                text_elements.append(text_el)
            else:
                translation_link.extract()
                translated_text_elements.append(text_el)

    html_elements = text_elements + additional_html_roots

    comment_text = get_display_text(text_elements) if text_elements else None
    comment_html = "".join(str(el) for el in html_elements)

    translated_comment_text = get_display_text(translated_text_elements)
    translated_comment_html = "".join(str(el) for el in translated_text_elements)
    translated_from = (
        translation_link.get_text().rsplit("from ", 1)[-1].strip()
        if translation_link
        else None
    )

    post = FacebookPostWithReaction(
        url=post_url,
        user_id=getattr(user, "id", ""),
        user_handle=getattr(user, "handle", ""),
        user_url=getattr(user, "url", ""),
        user_label=user_label,
        text=comment_text,
        html=comment_html,
        translated_text=translated_comment_text,
        translated_html=translated_comment_html,
        translated_from=translated_from,
        formatted_date=formatted_date,
        date=parsed_date,
        reactions=reactions,
        comments=comments,
        reactions_types=reactions_types,
    )
    return post


class FacebookMobileScraper(object):
    def __init__(self, cookie, throttle=FACEBOOK_MOBILE_DEFAULT_THROTTLE):

        # Grabbing cookie
        cookie = grab_facebook_cookie(cookie)

        if cookie is None:
            raise FacebookInvalidCookieError

        self.cookie = cookie
        self.pool = create_pool()

        self.rate_limiter_state = RateLimiterState(1, throttle)
        self.retryer = create_request_retryer()

    @rate_limited_method()
    @retrying_method()
    def request_page(self, url):
        error, result = request(
            url,
            pool=self.pool,
            cookie=self.cookie,
            headers={"User-Agent": "curl/7.68.0", "Accept-Language": "en"},
        )

        if error:
            raise error

        return result.data.decode("utf-8")

    def comments(self, url, detailed=False, per_call=False):

        if not has_facebook_comments(url):
            raise FacebookInvalidTargetError

        # Reformatting url to hit mobile website
        url = convert_url_to_mobile(url)

        def generator():
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
                    print(
                        "Could not process comment in %s" % current_url, file=sys.stderr
                    )
                    return

                calls += 1

                for reply_url, commented_id in data["replies"]:
                    url_queue.append((reply_url, None, commented_id))

                if data["next"] is not None:
                    url_queue.append((data["next"], data["direction"], in_reply_to))

                comments = data["comments"]

                for comment in data["comments"]:
                    if in_reply_to is not None:
                        replies += 1

                    if not per_call:
                        yield comment

                if per_call and len(comments) > 0:
                    if detailed:
                        details = {
                            "calls": calls,
                            "replies": replies,
                            "queue_size": len(url_queue),
                        }

                        yield details, comments
                    else:
                        yield comments

        return generator()

    def posts(self, url):
        parsed = parse_facebook_url(url)

        if not isinstance(parsed, ParsedFacebookGroup):
            raise FacebookInvalidTargetError

        url = convert_url_to_mobile(parsed.url)

        def generator():
            current_url = url

            while True:
                html = self.request_page(current_url)
                # with open("./dump.html", "w") as f:
                #     f.write(html)

                next_url, posts = scrape_posts(html)

                for post in posts:
                    yield post

                if next_url is None or len(posts) == 0:
                    break

                current_url = next_url

        return generator()

    def post(self, url):
        parsed = parse_facebook_url(url)

        if (
            not isinstance(parsed, ParsedFacebookPost)
            and not isinstance(parsed, ParsedFacebookVideo)
            and not isinstance(parsed, ParsedFacebookPhoto)
        ):
            raise FacebookNotPostError

        url = convert_url_to_mobile(parsed.url)

        html = self.request_page(url)

        return scrape_post(html)

    def post_author(self, url):
        if not has_facebook_comments(url):
            raise FacebookInvalidTargetError

        # Reformatting url to hit mobile website
        url = convert_url_to_mobile(url)

        html = self.request_page(url)
        soup = BeautifulSoup(html, "lxml")

        user_item = soup.select_one("[data-ft] h3 a[href]")

        if user_item is None:
            return None

        parsed = parse_facebook_url(user_item.get("href"), allow_relative_urls=True)
        user_label = user_item.get_text().strip()

        if isinstance(parsed, ParsedFacebookHandle):
            return FacebookUser(user_label, None, parsed.handle, parsed.url)
        elif isinstance(parsed, ParsedFacebookUser):
            return FacebookUser(user_label, parsed.id, parsed.handle, parsed.url)
        else:
            raise TypeError
