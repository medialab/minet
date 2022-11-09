# =============================================================================
# Minet Facebook Formatters
# =============================================================================
#
# Various formatters for Facebook data.
#
from casanova import namedrecord

from minet.facebook.constants import (
    FACEBOOK_COMMENT_CSV_HEADERS,
    FACEBOOK_POST_CSV_HEADERS,
    FACEBOOK_POST_WITH_REACTIONS_CSV_HEADERS,
)


FacebookComment = namedrecord("FacebookComment", FACEBOOK_COMMENT_CSV_HEADERS)
FacebookPost = namedrecord("FacebookPost", FACEBOOK_POST_CSV_HEADERS)
FacebookUser = namedrecord("FacebookUser", ["label", "id", "handle", "url"])
FacebookPostWithReaction = namedrecord(
    "FacebookPostWithReaction", FACEBOOK_POST_WITH_REACTIONS_CSV_HEADERS
)
