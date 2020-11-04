# =============================================================================
# Minet Facebook Formatters
# =============================================================================
#
# Various formatters for Facebook data.
#
from minet.facebook.constants import FACEBOOK_COMMENT_CSV_HEADERS


def format_comment(data):
    return [(data.get(key, '') or '') for key in FACEBOOK_COMMENT_CSV_HEADERS]
