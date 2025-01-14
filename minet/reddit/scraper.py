import re
from time import sleep
from ural import get_domain_name, urlpathsplit, is_url
from urllib.parse import urljoin

from minet.reddit.exceptions import RedditInvalidTargetError
from minet.reddit.types import (
    RedditPost,
    RedditComment,
    RedditUserPost,
    RedditUserComment,
)
from minet.web import request, create_pool_manager

ID_RE = re.compile(r"t1_(\w+)")


def add_slash(url: str):
    path = url.split("/")
    if path[-1] == "?limit=500":
        return url
    elif url[-1] != "/":
        return url + "/"
    return url


def resolve_relative_url(path):
    return urljoin("https://old.reddit.com", path)


def get_old_url(url):
    domain = get_domain_name(url)
    path = urlpathsplit(url)
    old_url = f"https://old.{domain}"
    for ele in path:
        old_url = urljoin(old_url, f"{ele}/")
    return old_url


def get_new_url(url):
    domain = get_domain_name(url)
    path = urlpathsplit(url)
    new_url = f"https://www.{domain}"
    for ele in path:
        new_url = urljoin(new_url, f"{ele}/")
    return new_url


def get_url_from_subreddit(name: str):
    if is_url(name):
        return name
    name = name.lstrip("/")
    if name.startswith("r/"):
        return urljoin("https://old.reddit.com/", name)
    return urljoin("https://old.reddit.com/r/", name)


def reddit_request(url, pool_manager):
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


def extract_t1_ids(text: str):
    ids = [match.group(1) for match in re.finditer(ID_RE, text)]
    if ids:
        return ids
    return text.split("'")[-4].split(",")


def get_current_id(com):
    current_id = com.get("id")
    if current_id:
        current_id = current_id.split("_")[-1]
    else:
        current_id = com.get("data-permalink").split("/")[-2]
    return current_id


def get_points(ele):
    scrapped_points = ele.select_one("[class='score unvoted']")
    score_hidden = ele.select_one("[class='score-hidden']")
    if not scrapped_points and not score_hidden:
        return "deleted"
    scrapped_points = ele.scrape_one("[class='score unvoted']", "title")
    if not scrapped_points:
        return "score hidden"
    return scrapped_points


def get_dates(ele):
    published_date = ele.scrape_one("time", "datetime")
    edited_date = ele.scrape_one("time.edited-timestamp", "datetime")
    return published_date, edited_date


def data_posts(
    post,
    title,
    url,
    author_text,
    points,
    scraped_number_comments,
    number_comments,
    published_date,
    edited_date,
    link,
    error,
):
    try_author = post.select_one("a[class*='author']")
    author = try_author.get_text() if try_author else "[Deleted]"
    if get_domain_name(link) == "reddit.com":
        link = ""
    data = RedditPost(
        title=title,
        url=get_new_url(url),
        author=author,
        author_text=author_text,
        points=points,
        scraped_number_comments=scraped_number_comments,
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
    scraped_number_comments,
    number_comments,
    published_date,
    edited_date,
    link,
    error,
):
    sub = post.scrape_one("a[class*='subreddit']", "href")
    data = RedditUserPost(
        title=title,
        url=get_new_url(url),
        author_text=author_text,
        points=points,
        scraped_number_comments=scraped_number_comments,
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

    def get_childs_l500(self, url, list_comments, parent_id):
        _, soup, _ = reddit_request(url, self.pool_manager)
        comments = soup.select("div.commentarea>div>div[class*='comment']")
        if parent_id is None:
            for com in comments:
                list_comments.append((None, com))
        else:
            for com in comments:
                child = com.find("div", class_="child")
                if child.text != "":
                    child = child.find("div")
                    child_com = child.find_all(
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
                    for ele in child_com:
                        list_comments.append((parent_id, ele))
        return list_comments

    def get_comments(self, url: str, all):
        m_comments = []
        old_url = get_old_url(url)
        url_limit = old_url + "?limit=500"
        _, soup, error = reddit_request(url_limit, self.pool_manager)
        if error:
            yield RedditComment(
                comment_url="",
                author="",
                id="",
                parent="",
                points="",
                published_date="",
                comment="",
                error=error,
            )
        else:
            first_comments = soup.select("div.commentarea>div>div[class*='comment']")
            if all:
                more = soup.select("div.commentarea>div>div[class*='morechildren']")
                for ele in more:
                    a = ele.select_one("a")
                    onclick = a["onclick"]
                    id_list = extract_t1_ids(onclick)
                    for id in id_list:
                        comment_url = f"{old_url}{id}/"
                        m_comments = self.get_childs_l500(comment_url, m_comments, None)
            for ele in first_comments:
                m_comments.append((None, ele))
            while m_comments:
                parent, com = m_comments.pop()
                current_id = get_current_id(com)
                if "deleted" in com.get("class") and "comment" in com.get("class"):
                    comment_url = com.get("data-permalink")
                    author = "[Deleted]"
                    points = None
                else:
                    comment_url = com.scrape_one("a.bylink", "href")
                    try_author = com.select_one("div.entry.unvoted")
                    author = try_author.scrape_one("a[class^='author']")
                    if not author:
                        author = "[Deleted]"
                    points = get_points(com)
                published_date, edited_date = get_dates(com)
                if "morerecursion" in com.get("class") and all:
                    url_rec = f"https://old.reddit.com{com.scrape_one('a', 'href')}"
                    m_comments = self.get_childs_l500(url_rec, m_comments, parent)
                elif "morechildren" in com.get("class") and all:
                    a = com.select_one("a")
                    onclick = a["onclick"]
                    id_list = extract_t1_ids(onclick)
                    for id in id_list:
                        comment_url = f"{old_url}{id}/"
                        m_comments = self.get_childs_l500(
                            comment_url, m_comments, current_id
                        )
                else:
                    child = com.find("div", class_="child")
                    if child.text != "":
                        child = child.find("div")
                        if all:
                            child_com = child.find_all(
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
                        else:
                            child_com = child.find_all(
                                "div",
                                class_=lambda x: x
                                and ("comment" in x or "deleted comment" in x),
                                recursive=False,
                            )
                        for ele in child_com:
                            m_comments.append((current_id, ele))
                    data = RedditComment(
                        comment_url=get_new_url(resolve_relative_url(comment_url)),
                        author=author,
                        id=current_id,
                        parent=parent,
                        points=points,
                        published_date=published_date,
                        edited_date=edited_date,
                        comment=com.scrape_one("div.md:not(div.child a)"),
                        error=error,
                    )
                    if data.id != "":
                        yield data

    def get_general_post(self, url: str, type: str, add_text: bool, limit: int):
        n_crawled = 0
        old_url = get_old_url(get_url_from_subreddit(url))
        while old_url and (limit is None or n_crawled < limit):
            if limit is not None and n_crawled == limit:
                break
            _, soup, error = reddit_request(old_url, self.pool_manager)
            posts = soup.select("div[id^='thing_t3_']")
            for post in posts:
                if limit is not None and n_crawled == limit:
                    break
                list_buttons = post.select_one("ul.flat-list.buttons")
                if len(list_buttons.scrape("span.promoted-span")) == 0:
                    title = post.force_select_one("a[class*='title']").get_text()
                    post_url = list_buttons.scrape_one(
                        "a[class^='bylink comments']", "href"
                    )
                    n_comments_scraped = list_buttons.select_one(
                        "a[class^='bylink comments']"
                    ).get_text()
                    match = re.match(r"(\d+)\s+comment(s)?", n_comments_scraped)
                    if match:
                        n_comments = int(match.group(1))
                    else:
                        n_comments = 0
                    upvote = get_points(post)
                    published_date, edited_date = get_dates(post)
                    link = resolve_relative_url(
                        post.scrape_one("a[class*='title']", "href")
                    )
                    if link == post_url:
                        link = ""
                    if add_text:
                        _, text_soup, text_error = reddit_request(
                            post_url, self.pool_manager
                        )
                        if text_error:
                            if type == "subreddit":
                                yield data_posts(
                                    post,
                                    title,
                                    post_url,
                                    "",
                                    upvote,
                                    n_comments_scraped,
                                    n_comments,
                                    published_date,
                                    edited_date,
                                    link,
                                    text_error,
                                )
                            else:
                                yield data_user_posts(
                                    post,
                                    title,
                                    post_url,
                                    "",
                                    upvote,
                                    n_comments_scraped,
                                    n_comments,
                                    published_date,
                                    edited_date,
                                    link,
                                    text_error,
                                )
                        try_content = text_soup.select_one(
                            "div#siteTable div[class^='usertext']"
                        )
                        if try_content:
                            content = try_content.get_text()
                        else:
                            content = ""
                    else:
                        content = ""
                    if type == "subreddit":
                        post = data_posts(
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
                    else:
                        post = data_user_posts(
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

                    yield post
                    n_crawled += 1
            old_url = soup.scrape_one("span.next-button a", "href")

    def get_user_comments(self, url: str, limit: int):
        n_crawled = 0
        old_url = get_old_url(url)
        while old_url and (limit is None or n_crawled < limit):
            if limit is not None and n_crawled == limit:
                break
            _, soup, error = reddit_request(old_url, self.pool_manager)
            if error:
                yield RedditUserComment(
                    post_title="",
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
                    post_title = comment.scrape_one("a.title")
                    post_url = comment.scrape_one("a.bylink.may-blank", "href")
                    post_author = comment.scrape_one("p.parent>a[class^='author']")
                    post_subreddit = comment.scrape_one("a[class^='subreddit']", "href")
                    points = get_points(comment)
                    published_date, edited_date = get_dates(comment)
                    text = comment.scrape_one("div.content div.md")
                    link = comment.scrape_one("div.content div.md a", "href")
                    comment_url = comment.scrape_one("a.bylink", "href")
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
