# =============================================================================
# Minet Instagram Formatters
# =============================================================================
#
# Various data formatters for Instagram data.
#
from casanova import namedrecord
from ebbe import getpath

from minet.instagram.constants import INSTAGRAM_POST_CSV_HEADERS

InstagramPost = namedrecord("InstagramPost", INSTAGRAM_POST_CSV_HEADERS)


def format_post(item):

    row = InstagramPost(
        item["id"],
        getpath(item, ["edge_media_to_caption", "edges", 0, "node", "text"]),
        item["owner"]["id"],
        item["shortcode"],
        item["edge_media_to_comment"]["count"],
        item["edge_liked_by"]["count"],
        item["edge_media_preview_like"]["count"],
        item["is_video"],
        item["accessibility_caption"],
        item["display_url"],
        item["comments_disabled"],
        item["__typename"],
        item["taken_at_timestamp"],
    )

    return row
