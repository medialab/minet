# =============================================================================
# Minet Hyphe Constants
# =============================================================================
#
# Bunch of Hyphe-related constants.
#
DEFAULT_WEBENTITY_PAGINATION_COUNT = 100
DEFAULT_PAGE_PAGINATION_COUNT = 500
DEFAULT_TIMEOUT = 10 * 60

WEBENTITY_STATUSES = set(["IN", "OUT", "UNDECIDED", "DISCOVERED"])

WEBENTITY_CSV_HEADERS = [
    "id",
    "name",
    "status",
    "pages",
    "homepage",
    "prefixes",
    "degree",
    "undirected_degree",
    "indegree",
    "outdegree",
]

PAGE_CSV_HEADERS = [
    "url",
    "lru",
    "webentity",
    "webentity_status",
    "status",
    "crawled",
    "encoding",
    "content_type",
    "crawl_timestamp",
    "crawl_datetime",
    "size",
    "error",
]
