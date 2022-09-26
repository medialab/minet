# =============================================================================
# Minet Instagram Formatters
# =============================================================================
#
# Various data formatters for Instagram data.
#
from casanova import namedrecord
from ebbe import getpath

from minet.instagram.constants import INSTAGRAM_POST_CSV_HEADERS

InstagramHashtag = namedrecord("InstagramHashtag", INSTAGRAM_POST_CSV_HEADERS)


def format_post(item):

    row = InstagramHashtag(
        item["comments_disabled"],
        item["__typename"],
        item["id"],
        getpath(item, ["edge_media_to_caption", "edges", 0, "node", "text"]),
        item["shortcode"],
        item["edge_media_to_comment"]["count"],
        item["taken_at_timestamp"],
        item["display_url"],
        item["edge_liked_by"]["count"],
        item["edge_media_preview_like"]["count"],
        item["owner"]["id"],
        item["is_video"],
        item["accessibility_caption"],
    )

    return row
