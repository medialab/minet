# =============================================================================
# Minet Hyphe Formatters
# =============================================================================
#
# Bunch of Hyphe-related formatters.
#
from datetime import datetime


def format_webentity_for_csv(webentity):
    return [
        webentity["id"],
        webentity["name"],
        webentity["status"],
        webentity["pages_total"],
        webentity["homepage"],
        " ".join(webentity["prefixes"]),
        webentity["indegree"] + webentity["outdegree"],
        webentity["undirected_degree"],
        webentity["indegree"],
        webentity["outdegree"],
    ]


def format_page_for_csv(webentity, page, filename=None):
    row = [
        page["url"],
        page["lru"],
        webentity["id"],
        webentity["status"],
        page.get("status", ""),
        "1" if page["crawled"] else "0",
        page.get("encoding", ""),
        page.get("content_type", ""),
        page["crawl_timestamp"] if "crawl_timestamp" in page else "",
        datetime.fromtimestamp(int(page["crawl_timestamp"]) / 1000).isoformat(
            timespec="seconds"
        )
        if "crawl_timestamp" in page
        else "",
        page.get("size", "") or "",
        page.get("error", ""),
    ]

    if filename:
        row.append(filename)

    return row
