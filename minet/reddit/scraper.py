from minet.web import request, create_pool_manager
from math import ceil
from ural import get_domain_name, urlpathsplit, is_url
from time import sleep
from minet.reddit.types import RedditPost, RedditComment, RedditUserPost, RedditUserComment
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


def data_posts(
    post, title, url, author_text, real_points, points, scraped_number_comments, number_comments, published_date, link
):
    try_author = post.select_one("a[class*='author']")
    author = try_author.get_text() if try_author else "Deleted"
    data = RedditPost(
        title=title,
        url=get_new_url(url),
        author=author,
        author_text=author_text,
        scraped_points=points,
        approximated_points=real_points,
        scraped_number_comments=scraped_number_comments,
        number_comments=number_comments,
        published_date=published_date,
        external_link=link,
    )
    return data


def data_user_posts(
    post, title, url, author_text, real_points, points, scraped_number_comments, number_comments, published_date, link
):
    sub = post.scrape_one("a[class*='subreddit']", "href")
    data = RedditUserPost(
        title=title,
        url=get_new_url(url),
        author_text=author_text,
        scraped_points=points,
        approximated_points=real_points,
        scraped_number_comments=scraped_number_comments,
        number_comments=number_comments,
        published_date=published_date,
        external_link=link,
        subreddit=sub,
    )
    return data


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

    def get_general_post(self, url: str, type: str, add_text: bool, nb=25):
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
                list_buttons = post.select_one("ul[class='flat-list buttons']")
                if len(list_buttons.scrape("span[class='promoted-span']")) == 0:
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
                    upvote = post.select_one("div[class='score unvoted']").get_text()
                    real_points = "" if upvote == "•" else upvote
                    if real_points[-1] == "k":
                        real_points = int(float(real_points[:-1]) * 1000)
                    published_date = post.scrape_one("time", "datetime")
                    link = resolve_relative_url(
                        post.scrape_one("a[class*='title']", "href")
                    )
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
                    if type == "subreddit":
                        post = data_posts(
                            post,
                            title,
                            post_url,
                            content,
                            real_points,
                            upvote,
                            n_comments_scraped,
                            n_comments,
                            published_date,
                            link,
                        )
                    else:
                        post = data_user_posts(
                            post,
                            title,
                            post_url,
                            content,
                            real_points,
                            upvote,
                            n_comments_scraped,
                            n_comments,
                            published_date,
                            link,
                        )

                    yield post
                n_crawled += 1
            old_url = soup.scrape("span[class='next-button'] a", "href")[0]

    def get_user_comments(self, url: str, nb=25):
        nb_pages = ceil(int(nb) / 25)
        n_crawled = 0
        old_url = get_old_url(url)
        for _ in range(nb_pages):
            if n_crawled == int(nb):
                break
            response = reddit_request(old_url, self.pool_manager)
            soup = response.soup()
            comments = soup.select("[data-type='comment']")
            for comment in comments:
                if n_crawled == int(nb):
                    break
                post_title = resolve_relative_url(comment.scrape_one("a[class='title']", "href"))
                post_author = comment.scrape_one("p[class='parent']>a[class^='author']", "href")
                post_subreddit = comment.scrape_one("a[class^='subreddit']", "href")
                points = comment.scrape_one("span[class='score unvoted']")
                published_date = comment.scrape_one("time", "datetime")
                text = comment.scrape_one("div[class='content'] div[class='md']")
                comment_url = comment.scrape_one("a[class='bylink']", "href")
                data = RedditUserComment(
                    post_title=post_title,
                    post_author=post_author,
                    post_subreddit=post_subreddit,
                    points=points,
                    published_date=published_date,
                    text=text,
                    comment_url=comment_url
                )
                yield data
                n_crawled += 1
