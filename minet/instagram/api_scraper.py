# =============================================================================
# Minet Instagram API Scraper
# =============================================================================
#
# Instagram public API "scraper".
#
import json
from urllib.parse import quote
from ebbe import getpath
import re
from json.decoder import JSONDecodeError
from ural.instagram import (
    parse_instagram_url,
    is_instagram_username,
    is_instagram_post_shortcode,
    InstagramPost as ParsedInstagramPost,
    InstagramUser as ParsedInstagramUser,
    InstagramReel as ParsedInstagramReel,
)
from minet.utils import sleep_with_entropy
from minet.cookies import coerce_cookie_for_url_from_browser
from minet.web import (
    create_pool_manager,
    create_request_retryer,
    request,
    retrying_method,
)
from minet.instagram.constants import (
    INSTAGRAM_DEFAULT_THROTTLE,
    INSTAGRAM_MAX_RANDOM_ADDENDUM,
    INSTAGRAM_NB_REQUEST_LITTLE_WAIT,
    INSTAGRAM_DEFAULT_THROTTLE_LITTLE_WAIT,
    INSTAGRAM_MAX_RANDOM_ADDENDUM_LITTLE_WAIT,
    INSTAGRAM_NB_REQUEST_BIG_WAIT,
    INSTAGRAM_DEFAULT_THROTTLE_BIG_WAIT,
    INSTAGRAM_MAX_RANDOM_ADDENDUM_BIG_WAIT,
    INSTAGRAM_MIN_TIME_RETRYER,
    INSTAGRAM_URL,
    INSTAGRAM_PUBLIC_API_DEFAULT_TIMEOUT,
)
from minet.instagram.exceptions import (
    InstagramError500,
    InstagramPublicAPIInvalidResponseError,
    InstagramInvalidCookieError,
    InstagramInvalidTargetError,
    InstagramTooManyRequestsError,
    InstagramNoPublicationError,
    InstagramPrivateOrNonExistentAccountError,
    InstagramHashtagNeverUsedError,
    InstagramAccountNoFollowError,
    InstagramPrivateAccountError,
)
from minet.instagram.formatters import (
    format_comment,
    format_hashtag_post,
    format_post,
    format_user,
    format_user_info,
)

INSTAGRAM_GRAPHQL_ENDPOINT = "https://www.instagram.com/graphql/query/"
INSTAGRAM_HASHTAG_QUERY_HASH = "9b498c08113f1e09617a1703c22b2f32"
INSTAGRAM_USER_ID_QUERY_HASH = "c9100bf9110dd6361671f113dd02e7d6"
INSTAGRAM_MAGIC_TOKEN_PATTERN = re.compile(r"\"X-IG-App-ID\"\s*:\s*\"(\d+)\"")
INSTAGRAM_ID_PATTERN = re.compile(r"\d+")
INSTAGRAM_GET_USER_ID_PATTERN = re.compile(r"\d+_(\d+)")


def forge_comments_url(
    post,
    comment_id=None,
    min_or_max_id=None,
):
    if comment_id is not None and min_or_max_id is not None:
        url = (
            "https://www.instagram.com/api/v1/media/%s/comments/%s/child_comments/?max_id=%s"
            % (post, comment_id, min_or_max_id)
        )
        return url

    if min_or_max_id is not None:
        url = (
            "https://www.instagram.com/api/v1/media/%s/comments/?min_id=%s&can_support_threading=true&permalink_enabled=false"
            % (post, min_or_max_id)
        )
        return url

    url = (
        "https://www.instagram.com/api/v1/media/%s/comments/?can_support_threading=true&permalink_enabled=false"
        % post
    )
    return url


def forge_hashtag_search_url(name, cursor=None, count=50):
    params = {"tag_name": name, "first": count}

    if cursor is not None:
        params["after"] = cursor

    url = INSTAGRAM_GRAPHQL_ENDPOINT + "?query_hash=%s&variables=%s" % (
        INSTAGRAM_HASHTAG_QUERY_HASH,
        quote(json.dumps(params)),
    )

    return url


def forge_post_url_from_id(post_id):
    return "https://www.instagram.com/api/v1/media/%s/info/" % post_id


def forge_post_url_from_shortcode(post_shortcode):
    return "https://www.instagram.com/p/%s/?__a=1&__d=dis" % post_shortcode


def forge_username_url(user_id):
    params = {"user_id": user_id, "include_reel": True}

    url = INSTAGRAM_GRAPHQL_ENDPOINT + "?query_hash=%s&variables=%s" % (
        INSTAGRAM_USER_ID_QUERY_HASH,
        quote(json.dumps(params)),
    )

    return url


def forge_user_url(name):
    return "https://i.instagram.com/api/v1/users/web_profile_info/?username=%s" % name


def forge_user_followers_url(
    id,
    count=50,
    max_id=None,
):
    url = (
        "https://i.instagram.com/api/v1/friendships/%s/followers/?count=%s&search_surface=follow_list_page"
        % (
            id,
            count,
        )
    )
    if max_id:
        url += "&max_id=%s" % max_id

    return url


def forge_user_following_url(
    id,
    count=50,
    max_id=None,
):
    url = (
        "https://i.instagram.com/api/v1/friendships/%s/following/?count=%s&search_surface=follow_list_page"
        % (
            id,
            count,
        )
    )
    if max_id:
        url += "&max_id=%s" % max_id

    return url


def forge_user_posts_url(name: str, count: int = 50, max_id=None, user_id=None) -> str:
    if max_id is not None:
        assert user_id is not None

        url = "https://i.instagram.com/api/v1/feed/user/%s/?count=%s&max_id=%s" % (
            user_id,
            count,
            max_id,
        )

        return url

    url = "https://i.instagram.com/api/v1/feed/user/%s/username/?count=%s" % (
        name,
        count,
    )

    return url


def ensure_magic_token(method):
    def wrapped(self, *args, **kwargs):
        if self.magic_token is None:
            self.get_magic_token()

        return method(self, *args, **kwargs)

    return wrapped


class InstagramAPIScraper(object):
    def __init__(self, cookie="firefox"):
        self.pool_manager = create_pool_manager(
            timeout=INSTAGRAM_PUBLIC_API_DEFAULT_TIMEOUT
        )

        cookie = coerce_cookie_for_url_from_browser(cookie, INSTAGRAM_URL)

        if not cookie:
            raise InstagramInvalidCookieError

        self.cookie = cookie
        self.magic_token = None
        self.nb_calls = 0
        self.retryer = create_request_retryer(
            min=INSTAGRAM_MIN_TIME_RETRYER,
            additional_exceptions=[InstagramTooManyRequestsError, InstagramError500],
        )

    @retrying_method()
    def request_json(self, url, magic_token=False):
        headers = {"Cookie": self.cookie}

        if magic_token:
            headers["X-IG-App-ID"] = self.magic_token

        response = request(
            url, pool_manager=self.pool_manager, spoof_ua=True, headers=headers
        )

        text = response.text()

        if (
            "the link you followed may be broken, or the page may have been removed"
            in text.lower().strip()
        ):
            raise InstagramInvalidTargetError

        try:
            data = json.loads(text)
        except JSONDecodeError:
            raise RuntimeError("HTML for the request to " + url + " : " + text)

        if response.status == 429:
            raise InstagramTooManyRequestsError

        if response.status == 500:
            raise InstagramError500

        if response.status >= 400:
            if data["message"].lower().strip() == "media not found or unavailable":
                raise InstagramInvalidTargetError

            raise InstagramPublicAPIInvalidResponseError(url, response.status, data)

        if self.nb_calls != 0 and (self.nb_calls % INSTAGRAM_NB_REQUEST_BIG_WAIT) == 0:
            sleep_with_entropy(
                INSTAGRAM_DEFAULT_THROTTLE_BIG_WAIT,
                INSTAGRAM_MAX_RANDOM_ADDENDUM_BIG_WAIT,
            )
            self.nb_calls += 1

            return data

        elif (
            self.nb_calls != 0
            and (self.nb_calls % INSTAGRAM_NB_REQUEST_LITTLE_WAIT) == 0
        ):
            sleep_with_entropy(
                INSTAGRAM_DEFAULT_THROTTLE_LITTLE_WAIT,
                INSTAGRAM_MAX_RANDOM_ADDENDUM_LITTLE_WAIT,
            )
            self.nb_calls += 1

            return data

        sleep_with_entropy(INSTAGRAM_DEFAULT_THROTTLE, INSTAGRAM_MAX_RANDOM_ADDENDUM)
        self.nb_calls += 1

        return data

    def get_magic_token(self):
        response = request("https://www.instagram.com/disney")

        if response.status >= 400:
            return None

        t = INSTAGRAM_MAGIC_TOKEN_PATTERN.search(response.text())
        if t is None:
            return None

        self.magic_token = t.group(1)
        return self.magic_token

    @ensure_magic_token
    def comments(self, post):
        if not INSTAGRAM_ID_PATTERN.match(post):
            parsed = parse_instagram_url(post)
            if isinstance(parsed, (ParsedInstagramPost, ParsedInstagramReel)):
                shortcode = parsed.id

            elif is_instagram_post_shortcode(post):
                shortcode = post

            else:
                raise InstagramInvalidTargetError

            url = forge_post_url_from_shortcode(shortcode)

            data_post = self.request_json(url, magic_token=True)
            if not data_post:
                raise InstagramInvalidTargetError

            post = getpath(data_post, ["items", 0, "pk"])

        min_id = None

        # NOTE: Instagram's comment pagination does not seem very consistent
        # so we cache the ids of already seen comments just to be on the safe
        # side here.
        # NOTE: this could become an issue if memory runs out, but better safe
        # than sorry for now...
        already_seen = set()

        while True:
            url = forge_comments_url(post, min_or_max_id=min_id)

            data = self.request_json(url, magic_token=True)

            if not data:
                break

            items = data.get("comments")

            if not items:
                break

            for item in items:
                if item.get("type") == 2:
                    continue

                if item["pk"] in already_seen:
                    continue

                already_seen.add(item["pk"])

                yield format_comment(item)

                if item.get("child_comment_count") > 0:
                    max_id = ""

                    while True:
                        url = forge_comments_url(
                            post, comment_id=item.get("pk"), min_or_max_id=max_id
                        )

                        data_comment = self.request_json(url, magic_token=True)

                        if not data_comment:
                            break

                        children_items = data_comment.get("child_comments")

                        for children_item in children_items:
                            yield format_comment(children_item)

                        more_available = data_comment.get(
                            "has_more_tail_child_comments"
                        )

                        if not more_available:
                            break

                        max_id = data_comment.get("next_max_child_cursor")

            min_id = data.get("next_min_id")

            if not min_id:
                break

    def search_hashtag(self, hashtag):
        hashtag = hashtag.lstrip("#")
        cursor = None

        while True:
            url = forge_hashtag_search_url(hashtag, cursor=cursor)

            data = self.request_json(url)

            if not getpath(data, ["data", "hashtag"]):
                raise InstagramHashtagNeverUsedError

            data = getpath(data, ["data", "hashtag", "edge_hashtag_to_media"])

            if not data:
                break

            edges = data.get("edges")

            for edge in edges:
                yield format_hashtag_post(edge["node"])

            has_next_page = getpath(data, ["page_info", "has_next_page"])

            if not has_next_page:
                break

            cursor = getpath(data, ["page_info", "end_cursor"])

    @ensure_magic_token
    def post_infos(self, name):
        if INSTAGRAM_ID_PATTERN.match(name):
            url = forge_post_url_from_id(name)

        else:
            parsed = parse_instagram_url(name)
            if isinstance(parsed, (ParsedInstagramPost, ParsedInstagramReel)):
                shortcode = parsed.id

            elif is_instagram_post_shortcode(name):
                shortcode = name

            else:
                raise InstagramInvalidTargetError

            url = forge_post_url_from_shortcode(shortcode)

        data = self.request_json(url, magic_token=True)

        if not data:
            raise InstagramInvalidTargetError

        return format_post(getpath(data, ["items", 0]))

    def get_username(self, name):
        if INSTAGRAM_ID_PATTERN.match(name):
            url = forge_username_url(name)

            data_user_id = self.request_json(url)

            if not data_user_id:
                raise InstagramInvalidTargetError

            name = getpath(data_user_id, ["data", "user", "reel", "user", "username"])

        else:
            parsed = parse_instagram_url(name)

            if isinstance(parsed, (ParsedInstagramPost, ParsedInstagramUser)):
                if not parsed.name:
                    raise InstagramInvalidTargetError

                name = parsed.name

            else:
                name = name.lstrip("@")

                if not is_instagram_username(name):
                    raise InstagramInvalidTargetError

        return name

    @ensure_magic_token
    def get_user(self, name):
        url = forge_user_url(name)

        return self.request_json(url, magic_token=True)

    @ensure_magic_token
    def user_followers(self, name):
        name = self.get_username(name)

        max_id = None
        data_user = self.get_user(name)
        user_id = getpath(data_user, ["data", "user", "id"])

        while True:
            url = forge_user_followers_url(user_id, max_id=max_id)

            data = self.request_json(url, magic_token=True)

            if not data:
                break

            items = data.get("users")

            if not items:
                followed_count = getpath(
                    data_user, ["data", "user", "edge_followed_by", "count"]
                )
                if followed_count:
                    raise InstagramPrivateAccountError(followed_count)

                raise InstagramAccountNoFollowError

            for item in items:
                yield format_user(item)

            max_id = data.get("next_max_id")

            if not max_id:
                break

    @ensure_magic_token
    def user_following(self, name):
        name = self.get_username(name)

        max_id = None
        data_user = self.get_user(name)
        user_id = getpath(data_user, ["data", "user", "id"])

        while True:
            url = forge_user_following_url(user_id, max_id=max_id)

            data = self.request_json(url, magic_token=True)

            if not data:
                break

            items = data.get("users")

            if not items:
                followers_count = getpath(
                    data_user, ["data", "user", "edge_follow", "count"]
                )
                if followers_count:
                    raise InstagramPrivateAccountError(followers_count)

                raise InstagramAccountNoFollowError

            for item in items:
                yield format_user(item)

            max_id = data.get("next_max_id")

            if not max_id:
                break

    @ensure_magic_token
    def user_posts(self, name):
        name = self.get_username(name)

        max_id = None
        user_id = None

        while True:
            url = forge_user_posts_url(name, max_id=max_id, user_id=user_id)

            data = self.request_json(url, magic_token=True)

            if not data:
                break

            # NOTE: user id must not be inferred from max_id because of
            # posts that were co-authored
            if user_id is None:
                user_id = data["user"]["pk"]

            items = data.get("items")

            if not items:
                if getpath(data, ["user", "username"]):
                    raise InstagramNoPublicationError

                raise InstagramPrivateOrNonExistentAccountError

            for item in items:
                yield format_post(item)

            more_available = data.get("more_available")

            if not more_available:
                break

            max_id = data.get("next_max_id")

    @ensure_magic_token
    def user_infos(self, name):
        name = self.get_username(name)

        data = self.get_user(name)

        if not data:
            raise InstagramInvalidTargetError

        user = getpath(data, ["data", "user"])

        if not user:
            raise InstagramInvalidTargetError

        return format_user_info(user)
