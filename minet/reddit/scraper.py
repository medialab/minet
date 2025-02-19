from typing import Tuple, List, Optional, Iterator, Union, Literal, overload

import re
from time import sleep
from ural import is_url
from urllib.parse import urljoin
from urllib3 import PoolManager

from minet.web import request, create_pool_manager, Response
from minet.scrape import WonderfulSoup, Tag

from minet.reddit.constants import OLD_REDDIT_BASE_URL
from minet.reddit.exceptions import RedditInvalidTargetError
from minet.reddit.types import (
    RedditPost,
    RedditComment,
    RedditUserPost,
    RedditUserComment,
)


ID_RE = re.compile(r"t1_(\w+)")
COMMENTS_NUMBER_RE = re.compile(r"(\d+)\s+comment(s)?")

PostType = Literal["subreddit", "user"]


# When missing a '/' at the end of an url, reddit will make a redirection and it will reduce by 2 the number of requests remaining
def add_slash(url: str) -> str:
    path = url.split("/")

    if path[-1] != "" and not path[-1].startswith("?"):
        return url + "/"

    return url


def resolve_relative_url(path: str) -> str:
    return urljoin(OLD_REDDIT_BASE_URL, path)


def get_old_url(url: str) -> str:
    return url.replace("www.reddit", "old.reddit")


def get_new_url(url: str) -> str:
    return url.replace("old.reddit", "www.reddit")


def ensure_subreddit_url(name: str) -> str:
    if is_url(name):
        return name

    name = name.lstrip("/")

    if name.startswith("r/"):
        return urljoin(OLD_REDDIT_BASE_URL, name)

    return urljoin(OLD_REDDIT_BASE_URL + "/r/", name)


# TODO: make this a retryable method
def reddit_request(
    url: str, pool_manager: PoolManager
) -> Tuple[Response, WonderfulSoup, Optional[str]]:
    while True:
        response = request(
            add_slash(url),
            pool_manager=pool_manager,
            spoof_ua=True,
        )

        soup = response.soup()

        remaining_requests = float(response.headers["x-ratelimit-remaining"])

        if response.status == 429 and remaining_requests > 1:
            sleep(1)
            continue

        if (
            response.status == 500
            and soup.scrape_one("img", "alt") == "you broke reddit"
        ):
            return response, soup, "broken page"

        if response.status == 404 and soup.scrape_one("img", "alt") == "banned":
            return response, soup, "banned"

        if (
            soup.scrape_one("span.pagename.selected") == "page not found"
            or "search?q=" in url
            and soup.scrape_one("p.error")
        ):
            raise RedditInvalidTargetError

        if remaining_requests == 1 or response.status == 429:
            time_remaining = int(response.headers["x-ratelimit-reset"])
            sleep(time_remaining)
            continue

        return response, soup, None


def extract_t1_ids(text: str) -> List[str]:
    ids = [match.group(1) for match in re.finditer(ID_RE, text)]

    if ids:
        return ids

    return text.split("'")[-4].split(",")


def get_current_id(comment_element: Tag) -> str:
    current_id = comment_element.get("id")

    if current_id:
        current_id = current_id.split("_")[-1]
    else:
        current_id = comment_element["data-permalink"].split("/")[-2]

    return current_id


def get_points(element: Tag) -> str:
    scrapped_points = element.select_one(".score.unvoted")
    score_hidden = element.select_one(".score-hidden")

    if not scrapped_points and not score_hidden:
        return "deleted"

    scrapped_points = element.scrape_one(".score.unvoted", "title")

    if not scrapped_points:
        return "score hidden"

    return scrapped_points


def get_dates(element: Tag) -> Tuple[Optional[str], Optional[str]]:
    published_date = element.scrape_one("time", "datetime")
    edited_date = element.scrape_one("time.edited-timestamp", "datetime")

    return published_date, edited_date


def data_posts(
    post,
    title,
    url,
    author_text,
    points,
    raw_number_comments,
    number_comments,
    published_date,
    edited_date,
    link,
    error,
) -> RedditPost:
    author = post.scrape_one("a.author")

    if "reddit.com/" in link:
        link = None

    data = RedditPost(
        title=title,
        url=get_new_url(url),
        author=author if author else "[Deleted]",
        author_text=author_text,
        points=points,
        raw_number_comments=raw_number_comments,
        number_comments=number_comments,
        published_date=published_date,
        edited_date=edited_date,
        external_link=link,
        error=error,
    )

    return data


def data_user_posts(
    post,
    title,
    url,
    author_text,
    points,
    raw_number_comments,
    number_comments,
    published_date,
    edited_date,
    link,
    error,
) -> RedditUserPost:
    sub = post.scrape_one("a.subreddit", "href")

    data = RedditUserPost(
        title=title,
        url=get_new_url(url),
        author_text=author_text,
        points=points,
        raw_number_comments=raw_number_comments,
        number_comments=number_comments,
        published_date=published_date,
        edited_date=edited_date,
        external_link=link,
        subreddit=get_new_url(sub),
        error=error,
    )

    return data


class RedditScraper(object):
    def __init__(self):
        self.pool_manager = create_pool_manager()

    # NOTE: this potentially mutates the given list!
    def get_childs_l500(
        self,
        url: str,
        list_comments: List[Tuple[Optional[str], Tag]],
        parent_id: Optional[str],
    ) -> List[Tuple[Optional[str], Tag]]:
        _, soup, _ = reddit_request(url, self.pool_manager)

        comments = soup.select("div.commentarea > div > div.comment")

        if parent_id is None:
            for comment in comments:
                list_comments.append((None, comment))

            return list_comments

        for comment in comments:
            child = comment.force_select_one("div.child")

            if child.text != "":
                child = child.force_find("div")
                child_comment = child.find_all(
                    "div",
                    class_=lambda x: x
                    and (
                        "comment" in x
                        or "deleted comment" in x
                        or "morerecursion" in x
                        or "morechildren" in x
                    ),
                    recursive=False,
                )

                for element in child_comment:
                    list_comments.append((parent_id, element))

        return list_comments

    def get_comments(self, url: str, all: bool = True) -> Iterator[RedditComment]:
        m_comments: List[Tuple[Optional[str], Tag]] = []

        old_url = get_old_url(url)
        url_limit = old_url + "?limit=500"

        _, soup, error = reddit_request(url_limit, self.pool_manager)

        # TODO: this should be an exception?
        if error:
            yield RedditComment(
                comment_url="",
                author="",
                id="",
                parent="",
                points="",
                published_date="",
                edited_date="",
                comment="",
                error=error,
            )

            return

        first_comments = soup.select("div.commentarea > div > div.comment")

        if all:
            more = soup.select("div.commentarea > div > div.morechildren")

            for element in more:
                a = element.force_select_one("a")
                onclick = a["onclick"]
                id_list = extract_t1_ids(onclick)

                for id in id_list:
                    comment_url = f"{old_url}{id}/"
                    m_comments = self.get_childs_l500(comment_url, m_comments, None)

        for element in first_comments:
            m_comments.append((None, element))

        while m_comments:
            parent, comment = m_comments.pop()
            current_id = get_current_id(comment)

            if "deleted" in comment["class"] and "comment" in comment["class"]:
                comment_url = comment["data-permalink"]
                author = "[Deleted]"
                points = None
            else:
                comment_url = comment.force_scrape_one("a.bylink", "href")
                author = comment.scrape_one("div.entry.unvoted a.author")
                if not author:
                    author = "[Deleted]"
                points = get_points(comment)

            published_date, edited_date = get_dates(comment)

            if "morerecursion" in comment["class"] and all:
                url_rec = f"https://old.reddit.com{comment.scrape_one('a', 'href')}"
                m_comments = self.get_childs_l500(url_rec, m_comments, parent)
            elif "morechildren" in comment["class"] and all:
                a = comment.force_select_one("a")
                onclick = a["onclick"]
                id_list = extract_t1_ids(onclick)
                for id in id_list:
                    comment_url = f"{old_url}{id}/"
                    m_comments = self.get_childs_l500(
                        comment_url, m_comments, current_id
                    )
            else:
                child = comment.force_select_one("div.child")

                if child.text != "":
                    child = child.force_find("div")
                    if all:
                        child_comment = child.find_all(
                            "div",
                            class_=lambda x: x
                            and (
                                "comment" in x
                                or "morerecursion" in x
                                or "morechildren" in x
                            ),
                            recursive=False,
                        )
                    else:
                        child_comment = child.find_all(
                            "div",
                            class_=lambda x: x and ("comment" in x),
                            recursive=False,
                        )
                    for element in child_comment:
                        m_comments.append((current_id, element))

                data = RedditComment(
                    comment_url=get_new_url(resolve_relative_url(comment_url)),
                    author=author if author else "[Deleted]",
                    id=current_id,
                    parent=parent,
                    points=points,
                    published_date=published_date,
                    edited_date=edited_date,
                    comment=comment.force_scrape_one("div.md:not(div.child a)"),
                    error=error,
                )

                if data.id != "":
                    yield data

    @overload
    def get_posts(
        self, url: str, type: Literal["subreddit"], add_text: bool, limit: int
    ) -> Iterator[RedditPost]: ...

    @overload
    def get_posts(
        self, url: str, type: Literal["user"], add_text: bool, limit: int
    ) -> Iterator[RedditUserPost]: ...

    def get_posts(
        self, url: str, type: PostType, add_text: bool, limit: int
    ) -> Iterator[Union[RedditPost, RedditUserPost]]:
        fn = data_posts if type == "subreddit" else data_user_posts
        n_crawled = 0
        old_url = get_old_url(ensure_subreddit_url(url))
        while old_url and (limit is None or n_crawled < limit):
            if limit is not None and n_crawled == limit:
                break
            _, soup, error = reddit_request(old_url, self.pool_manager)
            posts = soup.select("div[id^='thing_t3_']")
            for post in posts:
                if limit is not None and n_crawled == limit:
                    break
                list_buttons = post.force_select_one("ul.flat-list.buttons")
                if len(list_buttons.scrape("span.promoted-span")) == 0:
                    title = post.force_select_one("a.title").get_text()
                    post_url = list_buttons.force_scrape_one(
                        "a.bylink.comments", "href"
                    )
                    n_comments_scraped = list_buttons.force_select_one(
                        "a.bylink.comments"
                    ).get_text()
                    match = COMMENTS_NUMBER_RE.match(n_comments_scraped)
                    if match:
                        n_comments = int(match.group(1))
                    else:
                        n_comments = 0
                    upvote = get_points(post)
                    published_date, edited_date = get_dates(post)
                    link = resolve_relative_url(
                        post.force_scrape_one("a.title", "href")
                    )
                    if link == post_url:
                        link = ""
                    if add_text:
                        _, text_soup, text_error = reddit_request(
                            post_url, self.pool_manager
                        )
                        if text_error:
                            yield fn(
                                post,
                                title,
                                post_url,
                                None,
                                upvote,
                                n_comments_scraped,
                                n_comments,
                                published_date,
                                edited_date,
                                link,
                                text_error,
                            )
                        content = text_soup.scrape_one(
                            "div#siteTable div.usertext-body"
                        )
                    else:
                        content = ""
                    yield fn(
                        post,
                        title,
                        post_url,
                        content,
                        upvote,
                        n_comments_scraped,
                        n_comments,
                        published_date,
                        edited_date,
                        link,
                        error,
                    )
                    n_crawled += 1
            old_url = soup.scrape_one("span.next-button a", "href")

    def get_user_comments(self, url: str, limit: int) -> Iterator[RedditUserComment]:
        n_crawled = 0
        old_url = get_old_url(url)
        while old_url and (limit is None or n_crawled < limit):
            if limit is not None and n_crawled == limit:
                break
            _, soup, error = reddit_request(old_url, self.pool_manager)
            if error:
                yield RedditUserComment(
                    post_title="",
                    post_url="",
                    link="",
                    post_author="",
                    post_subreddit="",
                    points="",
                    published_date="",
                    edited_date="",
                    text="",
                    comment_url="",
                    error=error,
                )
            else:
                comments = soup.select("[data-type='comment']")
                for comment in comments:
                    if limit is not None and n_crawled == limit:
                        break
                    post_title = comment.force_scrape_one("a.title")
                    post_url = comment.force_scrape_one("a.bylink.may-blank", "href")
                    post_author = comment.force_scrape_one("p.parent>a.author")
                    post_subreddit = comment.force_scrape_one("a.subreddit", "href")
                    points = get_points(comment)
                    published_date, edited_date = get_dates(comment)
                    text = comment.force_scrape_one("div.content div.md")
                    link = comment.force_scrape_one("div.content div.md a", "href")
                    comment_url = comment.force_scrape_one("a.bylink", "href")
                    data = RedditUserComment(
                        post_title=post_title,
                        post_url=get_new_url(post_url),
                        post_author=post_author,
                        post_subreddit=get_new_url(post_subreddit),
                        points=points,
                        published_date=published_date,
                        edited_date=edited_date,
                        text=text,
                        link=link,
                        comment_url=get_new_url(comment_url),
                        error=error,
                    )
                    yield data
                    n_crawled += 1
            old_url = soup.scrape_one("span.next-button a", "href")
