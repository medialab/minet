from typing import Iterable, Iterator, TypeVar, Callable, Tuple, List, Optional

from urllib.parse import quote, unquote

from minet.fetch import multithreaded_fetch

from minet.wikipedia.types import Granularity, Agent, Access, WikipediaPageViewsItem

BASE_URL = "https://wikimedia.org/api/rest_v1"
THREADS = 10

ItemType = TypeVar("ItemType")


# NOTE: this is not a sure shot, but good enough for wikipedia names
def ensure_is_quoted(string: str) -> str:
    if string == unquote(string):
        return string

    return quote(string)


def build_pageviews_url(
    name: str,
    lang: str,
    start_date: str,
    end_date: str,
    access: Access = "all-access",
    agent: Agent = "all-agents",
    granularity: Granularity = "monthly",
) -> str:
    return "{base_url}/metrics/pageviews/per-article/{lang}.wikipedia/{access}/{agent}/{name}/{granularity}/{start_date}/{end_date}".format(
        base_url=BASE_URL,
        name=ensure_is_quoted(name),
        lang=lang,
        granularity=granularity,
        access=access,
        agent=agent,
        start_date=start_date,
        end_date=end_date,
    )


class WikimediaRestAPIClient(object):
    def pageviews(
        self,
        pages: Iterable[ItemType],
        start_date: str,
        end_date: str,
        access: Access = "all-access",
        agent: Agent = "all-agents",
        granularity: Granularity = "monthly",
        key: Optional[Callable[[ItemType], Tuple[str, str]]] = None,
        lang: Optional[str] = None,
    ) -> Iterator[Tuple[ItemType, List[WikipediaPageViewsItem]]]:
        def api_url_from_item(page) -> str:
            page = page if not callable(key) else key(page)

            if lang is not None:
                if not isinstance(page, tuple):
                    page = (lang, page)
                else:
                    page = (lang, page[1])

            return build_pageviews_url(
                lang=page[0],
                name=page[1],
                start_date=start_date,
                end_date=end_date,
                access=access,
                granularity=granularity,
                agent=agent,
            )

        for result in multithreaded_fetch(
            pages, key=api_url_from_item, threads=THREADS
        ):
            if result.error:
                raise result.error

            pageviews = []

            for item in result.response.json()["items"]:
                pageviews.append(
                    WikipediaPageViewsItem(
                        project=item["project"],
                        article=item["article"],
                        granularity=item["granularity"],
                        timestamp=int(item["timestamp"]),
                        access=item["access"],
                        agent=item["agent"],
                        views=item["views"],
                    )
                )

            yield result.item, pageviews
