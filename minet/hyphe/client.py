# =============================================================================
# Minet Hyphe API Client
# =============================================================================
#
# Client for the Hyphe API.
#
from minet.web import create_pool, request_jsonrpc
from minet.hyphe.constants import WEBENTITY_STATUSES, DEFAULT_PAGINATION_COUNT
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
        self.pool = create_pool()

    def call(self, method, *args, **kwargs):
        err, result = request_jsonrpc(
            self.endpoint, method, pool=self.pool, *args, **kwargs
        )

        if err:
            return err, None

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

        return None, result[0]

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
            err, result = self.call("ping", timeout=5)

            if result["result"] == "pong":
                return True

        raise HypheCouldNotStartCorpusError

    def ensure_is_started(self):
        err, result = self.call("start_corpus", password=self.password)

        if err:
            raise err

        # Corpus is already started
        if result["result"]["status"] == "ready":
            return True

        # Pinging until ready
        return self.ping_until_ready()

    def status(self):
        err, stats = self.call("get_status")

        if err:
            raise err

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

    def webentities(self, statuses=None):
        if not statuses:
            statuses = WEBENTITY_STATUSES

        for status in statuses:
            token = None
            next_page = None

            while True:
                if token is None:
                    err, result = self.call(
                        "store.get_webentities_by_status",
                        status=status,
                        count=DEFAULT_PAGINATION_COUNT,
                    )
                else:
                    err, result = self.call(
                        "store.get_webentities_page",
                        pagination_token=token,
                        n_page=next_page,
                    )

                if err:
                    raise err

                result = result["result"]

                for webentity in result["webentities"]:
                    yield webentity

                if "next_page" in result and result["next_page"]:
                    token = result["token"]
                    next_page = result["next_page"]
                else:
                    break

    def webentity_pages(self, webentity_id, include_body=False):
        token = None

        while True:
            err, result = self.call(
                "store.paginate_webentity_pages",
                webentity_id=webentity_id,
                count=DEFAULT_PAGINATION_COUNT,
                pagination_token=token,
                include_page_metas=True,
                include_page_body=include_body,
            )

            if err:
                raise err

            result = result["result"]

            for page in result["pages"]:
                yield page

            if "token" in result and result["token"]:
                token = result["token"]
            else:
                break
