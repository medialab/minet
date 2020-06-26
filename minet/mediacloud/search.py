# =============================================================================
# Minet Mediacloud Search
# =============================================================================
#
# Function related to stories searching.
#
from urllib.parse import quote_plus

from minet.utils import request_json
from minet.mediacloud.constants import (
    MEDIACLOUD_API_BASE_URL,
    MEDIACLOUD_DEFAULT_BATCH
)
from minet.mediacloud.exceptions import (
    MediacloudServerError
)
from minet.mediacloud.formatters import format_story
from minet.mediacloud.utils import get_last_processed_stories_id


def query_additions(query, collections=None):
    if collections is not None:
        query += ' AND ('
        query += ' OR '.join('tags_id_media:%s' % str(collection) for collection in collections)
        query += ')'

    return query


def url_forge(token, query, collections=None, count=False,
              last_processed_stories_id=None):

    url = '%s/stories_public/%s?key=%s' % (
        MEDIACLOUD_API_BASE_URL,
        'count' if count else 'list',
        token
    )

    query = query_additions(query, collections=collections)

    url += '&q=%s' % quote_plus(query)

    if not count:
        url += '&rows=%i' % MEDIACLOUD_DEFAULT_BATCH

        if last_processed_stories_id is not None:
            url += '&last_processed_stories_id=%i' % last_processed_stories_id

    return url


def mediacloud_search(http, token, query, count=False, collections=None, format='csv_dict_row'):

    def generator():
        last_processed_stories_id = None

        while True:
            url = url_forge(
                token,
                query,
                collections=collections,
                count=count,
                last_processed_stories_id=last_processed_stories_id
            )

            err, response, data = request_json(http, url)

            if err:
                raise err

            if response.status >= 500:
                raise MediacloudServerError(server_error=data.get('error'))

            if count:
                yield data['count']
                return

            for story in data:
                if format == 'csv_dict_row':
                    yield format_story(story, as_dict=True)
                elif format == 'csv_row':
                    yield format_story(story)
                else:
                    yield story

            last_processed_stories_id = get_last_processed_stories_id(data)

            if last_processed_stories_id is None:
                return

    if count:
        return next(generator())

    return generator()
