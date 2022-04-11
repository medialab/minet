# =============================================================================
# Minet Hyphe Constants
# =============================================================================
#
# Bunch of Hyphe-related constants.
#

WEBENTITY_STATUSES = set(["IN", "OUT", "UNDECIDED", "DISCOVERED"])

DEFAULT_PAGINATION_COUNT = 100

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
