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
# from minet.mediacloud.formatters import format_topic_story


def url_forge(token, query, count=False):

    url = '%s/stories_public/%s?key=%s' % (
        MEDIACLOUD_API_BASE_URL,
        'count' if count else 'list',
        token
    )

    url += '&q=%s' % quote_plus(query)

    if not count:
        url += '&rows=%i' % MEDIACLOUD_DEFAULT_BATCH

    return url


def mediacloud_search(http, token, query, count=False, format='csv_dict_row'):

    if count:
        url = url_forge(token, query, count=True)

        err, _, data = request_json(http, url)

        if err:
            raise err

        return data['count']

    raise TypeError

    # while True:
    #     url = url_forge(
    #         token,
    #         topic_id=topic_id,
    #         link_id=link_id,
    #         media_id=media_id,
    #         from_media_id=from_media_id,
    #     )

    #     err, _, data = request_json(http, url)

    #     if err:
    #         raise err

    #     if 'stories' not in data or len(data['stories']) == 0:
    #         return

    #     next_link_id = get_next_link_id(data)

    #     for story in data['stories']:
    #         if format == 'csv_dict_row':
    #             yield format_topic_story(story, next_link_id, as_dict=True)
    #         elif format == 'csv_row':
    #             yield format_topic_story(story, next_link_id)
    #         else:
    #             yield story

    #     if next_link_id is None:
    #         return

    #     link_id = next_link_id
