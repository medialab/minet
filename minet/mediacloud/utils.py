# =============================================================================
# Minet Mediacloud Utils
# =============================================================================
#
# Miscellaneous utility function used throughout the mediacloud package.
#
from minet.web import request_json
from minet.mediacloud.constants import MEDIACLOUD_API_BASE_URL
from minet.mediacloud.exceptions import MediacloudServerError


def get_next_link_id(data):

    if "link_ids" not in data:
        return None

    pagination = data["link_ids"]

    if not pagination.get("next"):
        return None

    return pagination["next"]


def explode_tags(data):
    tags = []
    tag_sets = []
    tags_ids = []
    tag_sets_ids = []

    for tag in data:
        tags.append(tag["tag"])
        tag_sets.append(tag["tag_set"])
        tags_ids.append(tag["tags_id"])
        tag_sets_ids.append(tag["tag_sets_id"])

    return tags, tag_sets, tags_ids, tag_sets_ids


def get_last_processed_stories_id(data):
    if not data:
        return None

    return data[-1]["processed_stories_id"]


def make_simple_call(
    pool, token, route, formatter, raw=False, arg=None, query=None, single=False
):
    url = MEDIACLOUD_API_BASE_URL + route

    if arg is not None:
        url += "/" + str(arg)

    url += "?key=%s" % token

    if query is not None:
        url += "&" + ("&".join("%s=%s" % (str(k), str(v)) for k, v in query.items()))

    err, response, data = request_json(url, pool=pool)

    if err:
        raise err

    if response.status >= 500:
        raise MediacloudServerError(server_error=data.get("error"))

    results = []

    for item in data:
        if not raw:
            item = formatter(item)

        results.append(item)

    if single:
        return results[0]

    return results
