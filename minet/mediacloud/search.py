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
from minet.mediacloud.formatters import format_story
from minet.mediacloud.utils import get_last_processed_stories_id


def url_forge(token, query, count=False, last_processed_stories_id=None):

    url = '%s/stories_public/%s?key=%s' % (
        MEDIACLOUD_API_BASE_URL,
        'count' if count else 'list',
        token
    )

    url += '&q=%s' % quote_plus(query)

    if not count:
        url += '&rows=%i' % MEDIACLOUD_DEFAULT_BATCH

        if last_processed_stories_id is not None:
            url += '&last_processed_stories_id=%i' % last_processed_stories_id

    return url


def mediacloud_search(http, token, query, count=False, format='csv_dict_row'):

    if count:
        url = url_forge(token, query, count=True)

        err, _, data = request_json(http, url)

        if err:
            raise err

        return data['count']

    def generator():
        last_processed_stories_id = None

        while True:
            url = url_forge(
                token,
                query,
                last_processed_stories_id=last_processed_stories_id
            )

            err, _, data = request_json(http, url)

            if err:
                raise err

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

    return generator()
