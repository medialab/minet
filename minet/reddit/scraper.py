from minet.web import request, create_pool_manager
from math import ceil
from ural import get_domain_name, urlpathsplit, is_url
from time import sleep
from minet.reddit.types import RedditPost
import re


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
    if response.status == 404 or soup.scrape("p[id='noresults']"):
        print("invalid url!")
        return
    remaining_requests = float(response.headers["x-ratelimit-remaining"])
    if remaining_requests == 1:
        time_remaining = int(response.headers["x-ratelimit-reset"])
        print(f"Time before next request : {time_remaining}s")
        sleep(time_remaining)
        return reddit_request(url)
    if response.status == 429:
        return reddit_request(url)
    return response


class RedditScraper(object):
    def __init__(self):
        self.pool_manager = create_pool_manager()

    def get_posts(self, url, nb_post=25):
        list_posts = []
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
                list_buttons = post.select_one("ul[class='flat-list buttons']")
                if len(list_buttons.scrape("span[class='promoted-span']")) == 0:
                    title = post.force_select_one("a[class*='title']").get_text()
                    post_url = list_buttons.scrape_one(
                        "a[class^='bylink comments']", "href"
                    )
                    n_comments = list_buttons.select_one(
                        "a[class^='bylink comments']").get_text()
                    match = re.match(r"(\d+)\s+comments", n_comments)
                    if match:
                        n_comments = int(match.group(1))
                    else:
                        n_comments = 0
                    try_author = post.select_one("a[class*='author']")
                    author = try_author.get_text() if try_author else "Deleted"
                    upvote = post.select_one("div[class='score unvoted']").get_text()
                    published_date = post.scrape_one("time", "datetime")
                    link = post.scrape_one("a[class*='title']", "href")

                    data = RedditPost(
                        title=title,
                        url=post_url,
                        author=author,
                        author_text=None,
                        upvote=upvote,
                        number_comments=n_comments,
                        published_date=published_date,
                        link=link,
                    )

                    list_posts.append(data)
                    n_crawled += 1
            old_url = soup.scrape("span[class='next-button'] a", "href")[0]
        return list(list_posts)
