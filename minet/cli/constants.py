# =============================================================================
# Minet CLI Constants
# =============================================================================
#
# Miscellaneous cli-related constants.
#
DEFAULT_CONTENT_FOLDER = "downloaded"
DEFAULT_PREBUFFER_BYTES = 3_000_000  # 3mb

DEFAULT_CRAWLER_CAST = {
    "id": str,
    "parent": str,
    "spider": str,
    "depth": int,
    "url": str,
    "resolved_url": str,
    "error": str,
    "status": int,
    "degree": int,
    "body_size": int,
    "relevant": bool,
    "matches": int
}
