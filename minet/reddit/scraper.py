from minet.web import request, create_pool_manager
from math import ceil
from ural import get_domain_name, urlpathsplit, is_url
from time import sleep
from minet.reddit.types import RedditPost, RedditComment, RedditUserPost
from minet.reddit.exceptions import RedditInvalidTargetError
import re
from urllib.parse import urljoin


def resolve_relative_url(path):
    return urljoin("https://old.reddit.com", path)


def get_old_url(url):
    domain = get_domain_name(url)
    path = urlpathsplit(url)
    return f"https://old.{domain}/" + "/".join(path) + "/"


def get_new_url(url):
    domain = get_domain_name(url)
    path = urlpathsplit(url)
    return f"https://www.{domain}/" + "/".join(path) + "/"


def get_url_from_subreddit(name: str):
    if is_url(name):
        return name
    name = name.lstrip("/")
    if name.startswith("r/"):
        return "https://old.reddit.com/" + name
    return "https://old.reddit.com/r/" + name


def reddit_request(url, pool_manager):
    sleep(1)
    response = request(url, pool_manager=pool_manager)
    soup = response.soup()
    if response.status == 404 or (
        soup.scrape("p[id='noresults']") and not soup.scrape("div[class='commentarea']")
    ):
        raise RedditInvalidTargetError
    remaining_requests = float(response.headers["x-ratelimit-remaining"])
    if remaining_requests == 1:
        time_remaining = int(response.headers["x-ratelimit-reset"])
        print(f"Time before next request : {time_remaining}s")
        sleep(time_remaining)
        return reddit_request(url)
    if response.status == 429:
        return reddit_request(url)
    return response


def extract_t1_ids(text):
    pattern = r"t1_(\w+)"
    return [match.group(1) for match in re.finditer(pattern, text)]


def get_current_id(com):
    current_id = com.get("id")
    if current_id:
        current_id = current_id.split("_")[-1]
    else:
        current_id = com.get("data-permalink").split("/")[-2]
    return current_id


class RedditScraper(object):
    def __init__(self):
        self.pool_manager = create_pool_manager()

    def get_childs_l500(self, url, list_comments, parent_id):
        response = reddit_request(url, self.pool_manager)
        soup = response.soup()
        comments = soup.select("div[class='commentarea']>div>div[class*='comment']")
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

    def get_post_standard_info(self, post, add_text):
        list_buttons = post.select_one("ul[class='flat-list buttons']")
        if len(list_buttons.scrape("span[class='promoted-span']")) == 0:
            title = post.force_select_one("a[class*='title']").get_text()
            post_url = list_buttons.scrape_one("a[class^='bylink comments']", "href")
            n_comments = list_buttons.select_one(
                "a[class^='bylink comments']"
            ).get_text()
            match = re.match(r"(\d+)\s+comments", n_comments)
            if match:
                n_comments = int(match.group(1))
            else:
                n_comments = 0
            upvote = post.select_one("div[class='score unvoted']").get_text()
            if upvote == "•":
                upvote = ""
            published_date = post.scrape_one("time", "datetime")
            link = resolve_relative_url(post.scrape_one("a[class*='title']", "href"))
            if link == post_url:
                link = ""
            if add_text:
                text_response = reddit_request(post_url, self.pool_manager)
                text_soup = text_response.soup()
                try_content = text_soup.select_one(
                    "div[id='siteTable'] div[class^='usertext']"
                )
                if try_content:
                    content = try_content.get_text()
                else:
                    content = ""
            else:
                content = ""

            data = {
                "title": title,
                "url": post_url,
                "author_text": content,
                "points": upvote,
                "number_comments": n_comments,
                "published_date": published_date,
                "link": link,
            }
            return data

    def get_posts(self, url: str, add_text: bool, nb_post=25):
        nb_pages = ceil(int(nb_post) / 25)
        old_url = get_old_url(get_url_from_subreddit(url))
        n_crawled = 0
        for _ in range(nb_pages):
            if n_crawled == int(nb_post):
                break
            response = reddit_request(old_url, self.pool_manager)
            soup = response.soup()
            posts = soup.select("div[id^='thing_t3_']")
            for post in posts:
                if n_crawled == int(nb_post):
                    break
                data = self.get_post_standard_info(post, add_text)
                if data:
                    try_author = post.select_one("a[class*='author']")
                    author = try_author.get_text() if try_author else "Deleted"
                    post = RedditPost(
                        title=data["title"],
                        url=data["url"],
                        author=author,
                        author_text=data["author_text"],
                        points=data["points"],
                        number_comments=data["number_comments"],
                        published_date=data["published_date"],
                        external_link=data["link"],
                    )
                    yield post
                n_crawled += 1
            old_url = soup.scrape("span[class='next-button'] a", "href")[0]

    def get_comments(self, url: str, all):
        m_comments = []
        old_url = get_old_url(url)
        url_limit = old_url + "?limit=500"
        response = reddit_request(url_limit, self.pool_manager)
        soup = response.soup()
        first_comments = soup.select(
            "div[class='commentarea']>div>div[class*='comment']"
        )
        for ele in first_comments:
            m_comments.append((None, ele))
        while m_comments:
            parent, com = m_comments.pop()
            current_id = get_current_id(com)
            comment_url = com.scrape_one("a[class='bylink']", "href")
            try_author = com.scrape_one("a[class^='author']", "href")
            author = try_author if try_author else "Deleted"
            com_points = com.scrape_one("span[class='score unvoted']")
            match = re.search(r"-?\d+\s+point(?:s)?", com_points)
            com_points = int(re.search(r"-?\d+", match.group()).group())
            published_date = com.scrape_one("time", "datetime")
            if "morerecursion" in com.get("class") and all:
                url_rec = f"https://old.reddit.com{com.scrape_one('a', 'href')}"
                m_comments = self.get_childs_l500(url_rec, m_comments, parent)
            elif "morechildren" in com.get("class") and all:
                a = com.select_one("a")
                onclick = a["onclick"]
                id_list = extract_t1_ids(onclick)
                for id in id_list:
                    comment_url = f"{old_url}{id}"
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
                    comment_url=comment_url,
                    author=author,
                    id=current_id,
                    parent=parent,
                    points=com_points,
                    published_date=published_date,
                    comment=com.scrape_one("div[class='md']:not(div.child a)"),
                )
                if data.id != "":
                    yield data

    def get_user_posts(self, url: str, add_text: bool, nb=25):
        nb_pages = ceil(int(nb) / 25)
        n_crawled = 0
        old_url = get_old_url(url)
        for _ in range(nb_pages):
            if n_crawled == int(nb):
                break
            response = reddit_request(old_url, self.pool_manager)
            soup = response.soup()
            posts = soup.select("div[id^='thing_t3_']")
            for post in posts:
                if n_crawled == int(nb):
                    break
                data = self.get_post_standard_info(post, add_text)
                if data:
                    sub = post.scrape_one("a[class*='subreddit']", "href")
                    post = RedditUserPost(
                        title=data["title"],
                        url=data["url"],
                        author_text=data["author_text"],
                        points=data["points"],
                        number_comments=data["number_comments"],
                        published_date=data["published_date"],
                        external_link=data["link"],
                        subreddit=sub,
                    )
                    yield post
                n_crawled += 1
            old_url = soup.scrape("span[class='next-button'] a", "href")[0]

    # def get_user_comments(self, url: str, nb=25):
    #     old_url = get_old_url(url)
