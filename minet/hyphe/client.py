# =============================================================================
# Minet Hyphe API Client
# =============================================================================
#
# Client for the Hyphe API.
#
from minet.web import create_pool_manager, request_jsonrpc
from minet.hyphe.constants import (
    WEBENTITY_STATUSES,
    DEFAULT_WEBENTITY_PAGINATION_COUNT,
    DEFAULT_PAGE_PAGINATION_COUNT,
    DEFAULT_TIMEOUT,
)
from minet.hyphe.exceptions import (
    HypheCouldNotStartCorpusError,
    HypheJSONRPCError,
    HypheRequestFailError,
    HypheCorpusAuthenticationError,
)


class HypheAPIClient(object):
    def __init__(self, endpoint):
        if not endpoint.endswith("/"):
            endpoint += "/"

        self.endpoint = endpoint
        self.pool_manager = create_pool_manager(timeout=DEFAULT_TIMEOUT)

    def call(self, method, *args, **kwargs):
        response = request_jsonrpc(
            self.endpoint, method, pool_manager=self.pool_manager, *args, **kwargs
        )

        result = response.json()

        if "fault" in result:
            return HypheJSONRPCError(result), None

        if (
            isinstance(result, list)
            and len(result) > 0
            and isinstance(result[0], dict)
            and result[0].get("code") == "fail"
        ):
            msg = result[0].get("message", "")

            if "password" in msg:
                raise HypheCorpusAuthenticationError

            raise HypheRequestFailError(msg)

        return result[0]

    def corpus(self, corpus, password=None):
        return HypheAPIClientCorpus(self, corpus, password)


class HypheAPIClientCorpus(object):
    def __init__(self, client, corpus, password=None):
        self.client = client
        self.corpus = corpus
        self.password = password

    def call(self, method, *args, **kwargs):
        kwargs["corpus"] = self.corpus

        return self.client.call(method, *args, **kwargs)

    def ping_until_ready(self, max_attempts=10):
        for _ in range(max_attempts):
            result = self.call("ping", timeout=5)

            if result["result"] == "pong":
                return True

        raise HypheCouldNotStartCorpusError

    def ensure_is_started(self):
        result = self.call("start_corpus", password=self.password)

        # Corpus is already started
        if result["result"]["status"] == "ready":
            return True

        # Pinging until ready
        return self.ping_until_ready()

    def status(self):
        stats = self.call("get_status")

        return stats

    def count(self, statuses=None):
        if not statuses:
            statuses = WEBENTITY_STATUSES

        stats = self.status()

        webentity_counts = stats["result"]["corpus"]["traph"]["webentities"]

        total = 0

        for status in statuses:
            total += webentity_counts[status]

        info = {
            "webentities": total,
            "pages": stats["result"]["corpus"]["crawler"]["pages_found"],
        }

        return info

    def webentities(
        self, statuses=None, count: int = DEFAULT_WEBENTITY_PAGINATION_COUNT
    ):
        if not statuses:
            statuses = WEBENTITY_STATUSES

        for status in statuses:
            token = None
            next_page = None

            while True:
                if token is None:
                    result = self.call(
                        "store.get_webentities_by_status",
                        status=status,
                        count=count,
                    )
                else:
                    result = self.call(
                        "store.get_webentities_page",
                        pagination_token=token,
                        n_page=next_page,
                    )

                result = result["result"]

                for webentity in result["webentities"]:
                    yield webentity

                if "next_page" in result and result["next_page"]:
                    token = result["token"]
                    next_page = result["next_page"]
                else:
                    break

    def webentity_pages(
        self,
        webentity_id,
        include_body: bool = False,
        count: int = DEFAULT_PAGE_PAGINATION_COUNT,
    ):
        token = None

        while True:
            result = self.call(
                "store.paginate_webentity_pages",
                webentity_id=webentity_id,
                count=count,
                pagination_token=token,
                include_page_metas=True,
                include_page_body=include_body,
            )

            result = result["result"]

            for page in result["pages"]:
                yield page

            if "token" in result and result["token"]:
                token = result["token"]
            else:
                break
