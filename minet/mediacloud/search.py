# =============================================================================
# Minet Mediacloud Search
# =============================================================================
#
# Function related to stories searching.
#
from urllib.parse import quote_plus

from minet.web import request_json
from minet.mediacloud.constants import MEDIACLOUD_API_BASE_URL, MEDIACLOUD_DEFAULT_BATCH
from minet.mediacloud.exceptions import MediacloudServerError
from minet.mediacloud.formatters import format_story
from minet.mediacloud.utils import get_last_processed_stories_id


def create_plural_query_component(field, values):
    query = " AND ("
    query += " OR ".join(("%s:%s" % (field, str(value))) for value in values)
    query += ")"

    return query


def pad_date(string):
    if len(string) == 4:
        return string + "-01-01T00:00:00Z"

    if len(string) == 7:
        return string + "-01T00:00:00Z"

    if "T" not in string:
        return string + "T00:00:00Z"

    return string


def query_additions(
    query,
    collections=None,
    medias=None,
    publish_day=None,
    publish_month=None,
    publish_year=None,
):

    if collections is not None:
        query += create_plural_query_component("tags_id_media", collections)

    if medias is not None:
        query += create_plural_query_component("media_id", medias)

    if publish_day is not None:
        query += ' AND publish_day:"%s"' % pad_date(publish_day)

    if publish_month is not None:
        query += ' AND publish_month:"%s"' % pad_date(publish_month)

    if publish_year is not None:
        query += ' AND publish_year:"%s"' % pad_date(publish_year)

    # NOTE: range queries can be made with [from_date TO to_date] but must appear in filter

    return query


def url_forge(
    token,
    query,
    filter_query=None,
    collections=None,
    medias=None,
    publish_day=None,
    publish_month=None,
    publish_year=None,
    count=False,
    last_processed_stories_id=None,
):

    url = "%s/stories_public/%s?key=%s" % (
        MEDIACLOUD_API_BASE_URL,
        "count" if count else "list",
        token,
    )

    query = query_additions(
        query,
        collections=collections,
        medias=medias,
        publish_day=publish_day,
        publish_month=publish_month,
        publish_year=publish_year,
    )

    url += "&q=%s" % quote_plus(query)

    if filter_query is not None:
        url += "&fq=%s" % quote_plus(filter_query)

    if not count:
        url += "&rows=%i" % MEDIACLOUD_DEFAULT_BATCH

        if last_processed_stories_id is not None:
            url += "&last_processed_stories_id=%i" % last_processed_stories_id

    return url


def mediacloud_search(
    pool,
    token,
    query,
    filter_query=None,
    count=False,
    collections=None,
    medias=None,
    publish_day=None,
    publish_month=None,
    publish_year=None,
    raw=False,
):
    def generator():
        last_processed_stories_id = None

        while True:
            url = url_forge(
                token,
                query,
                filter_query=filter_query,
                collections=collections,
                medias=medias,
                publish_day=publish_day,
                publish_month=publish_month,
                publish_year=publish_year,
                count=count,
                last_processed_stories_id=last_processed_stories_id,
            )

            err, response, data = request_json(url, pool=pool)

            if err:
                raise err

            if response.status >= 500:
                raise MediacloudServerError(server_error=data.get("error"))

            if count:
                yield data["count"]
                return

            for story in data:
                if not raw:
                    story = format_story(story)

                yield story

            last_processed_stories_id = get_last_processed_stories_id(data)

            if last_processed_stories_id is None:
                return

    if count:
        return next(generator())

    return generator()
