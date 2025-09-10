from typing import Optional, List, Tuple

from ural import URLFormatter, urlpathsplit

from minet.bluesky.constants import (
    BLUESKY_HTTP_API_BASE_URL,
    BLUESKY_HTTP_API_ALTERNATE_URL,
)


def parse_post_url(url: str) -> Tuple[str, str]:
    path = urlpathsplit(url)

    did = path[1]
    rkey = path[3]

    return did, rkey


def format_post_at_uri(did: str, rkey: str) -> str:
    return "at://{}/app.bsky.feed.post/{}".format(did, rkey)


class BlueskyHTTPAPIUrlFormatter(URLFormatter):
    BASE_URL = BLUESKY_HTTP_API_BASE_URL

    def create_session(self) -> str:
        return self.format(
            path="com.atproto.server.createSession",
        )

    def refresh_session(self) -> str:
        return self.format(path="com.atproto.server.refreshSession")

    def resolve_handle(self, handle: str, _alternate_api=False) -> str:
        # Handles resolving of special handles based on a different DNS do not work on the regular API, we need to use the alternate endpoint from the public facing API
        # cf https://github.com/bluesky-social/indigo/issues/833
        return self.format(
            base_url=BLUESKY_HTTP_API_ALTERNATE_URL if _alternate_api else BLUESKY_HTTP_API_BASE_URL,
            path="com.atproto.identity.resolveHandle",
            args={"handle": handle},
        )

    def get_posts(self, uris: List[str]) -> str:
        return self.format(
            path="app.bsky.feed.getPosts", args=[("uris", uri) for uri in uris]
        )

    def get_profiles(self, identifiers: List[str]) -> str:
        return self.format(
            path="app.bsky.actor.getProfiles",
            args=[("actors", identifier) for identifier in identifiers],
        )

    def search_posts(
        self,
        q: str,
        cursor: Optional[str] = None,
        limit: int = 100,
        lang: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        mentions: Optional[str] = None,
        author: Optional[str] = None,
        domain: Optional[str] = None,
        url: Optional[str] = None,
        tag: Optional[List[str]] = None,
        not_keywords: Optional[List[str]] = None,
    ) -> str:
        args = {"q": q, "cursor": cursor, "limit": limit}

        if lang:
            args["lang"] = lang
        if since:
            args["since"] = since
        if until:
            args["until"] = until
        if mentions:
            args["mentions"] = mentions
        if author:
            args["author"] = author
        if domain:
            args["domain"] = domain
        if url:
            args["url"] = url
        if tag:
            # TODO : use the tag argument of the API properly, as for now it seems to not work at all. An issue has been opened on the Bluesky repo about it: https://github.com/bluesky-social/atproto/issues/3301
            # args["tag"] = tag
            # NOTE : we add the hashtags to the query instead, as it works in classic search syntax.
            for hashtag in tag:
                args["q"] += f" #{hashtag}"
        if not_keywords:
            # NOTE : we add the not_keywords to the query instead, as it works in classic search syntax.
            for not_keyword in not_keywords:
                args["q"] += f" -{not_keyword}"

        return self.format(
            path="app.bsky.feed.searchPosts",
            args=args,
        )

    def get_user_posts(
        self,
        identifier: str,
        cursor: Optional[str] = None,
        filter: Optional[str] = None,
        limit: int = 100,
    ) -> str:
        return self.format(
            path="app.bsky.feed.getAuthorFeed",
            args={
                "actor": identifier,
                "cursor": cursor,
                "filter": filter,
                "limit": limit,
            },
        )
