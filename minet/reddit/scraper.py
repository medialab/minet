from minet.web import request, create_pool_manager
from math import ceil
from ural import get_domain_name, urlpathsplit, is_url
from time import sleep
from minet.reddit.types import RedditPost
import json
from ebbe import getpath
from collections import deque
from urllib.parse import urljoin
import csv
import re
import sys
import os

def get_old_url(url):
    domain = get_domain_name(url)
    path = urlpathsplit(url)
    return f"https://old.{domain}/" + "/".join(path) + "/"


def get_new_url(url):
    domain = get_domain_name(url)
    path = urlpathsplit(url)
    return f"https://www.{domain}/" + "/".join(path) + "/"

def reddit_request(url, pool_manager):
    sleep(1)
    response = request(url, pool_manager=pool_manager)
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

    def get_posts_urls(self, url, nb_post = 25):
        dir_name = urlpathsplit(url)[1]
        try:
            os.mkdir(dir_name)
        except FileExistsError:
            pass
        except PermissionError:
            print(f"Permission denied: Unable to create '{dir_name}'.")
        except Exception as e:
            print(f"An error occurred: {e}")
        list_posts = set()
        nb_pages = ceil(int(nb_post) / 25)
        old_url = get_old_url(url)
        n_crawled = 0
        for _ in range(nb_pages):
            if n_crawled == int(nb_post):
                break
            response = reddit_request(old_url, self.pool_manager)
            soup = response.soup()
            list_buttons = soup.select("ul[class='flat-list buttons']")
            for link in list_buttons:
                if n_crawled == int(nb_post):
                    break
                if len(link.scrape("span[class='promoted-span']")) == 0:
                    list_posts.update(link.scrape("a[class^='bylink comments']", "href"))
                    n_crawled += 1
            old_url = soup.scrape("span[class='next-button'] a", "href")[0]
        return list(list_posts)


    def get_posts(self, url, nb_post):
        posts = []
        list_posts_url = self.get_posts_urls(self, url, nb_post)
        for url in list_posts_url:
            response = reddit_request(url, self.pool_manager)
            if response.url == 429:
                print(response.headers)
                print(response.end_url)
            soup = response.soup()
            title = soup.force_select_one("a[class^='title']").get_text()
            upvote = soup.force_select_one("div[class='score'] span").get_text()
            author = soup.scrape_one("a[class^='author']", "href")
            published_date = soup.scrape_one("div[class='date'] time", "datetime")
            link = soup.scrape_one("a[class^='title']", "href")
            if urlpathsplit(link) == urlpathsplit(url):
                link = None
            author_text = soup.scrape_one(
                "div[id='siteTable'] div[class^='usertext-body'] div p"
            )
            post = RedditPost(
                title=title,
                url=url,
                author=author,
                author_text=author_text,
                upvote=upvote,
                published_date=published_date,
                link=link,
            )
            posts.append(post)
        return posts