# =============================================================================
# Minet CrowdTangle Formatters
# =============================================================================
#
# Various data formatters for CrowdTangle API data.
#
from casanova import namedrecord

from minet.crowdtangle.constants import (
    CROWDTANGLE_POST_TYPES,
    CROWDTANGLE_REACTION_TYPES,
    CROWDTANGLE_POST_CSV_HEADERS,
    CROWDTANGLE_POST_CSV_HEADERS_WITH_LINK,
    CROWDTANGLE_SUMMARY_CSV_HEADERS,
    CROWDTANGLE_LEADERBOARD_CSV_HEADERS,
    CROWDTANGLE_LEADERBOARD_CSV_HEADERS_WITH_BREAKDOWN,
    CROWDTANGLE_LIST_CSV_HEADERS,
    CROWDTANGLE_STATISTICS,
    CROWDTANGLE_FULL_STATISTICS,
)

CrowdTanglePost = namedrecord(
    "CrowdTanglePost",
    CROWDTANGLE_POST_CSV_HEADERS,
    boolean=["account_verified"],
    plural=["links", "expanded_links"],
    json=["media"],
)

CrowdTanglePostWithLink = namedrecord(
    "CrowdTanglePostWithLink",
    CROWDTANGLE_POST_CSV_HEADERS_WITH_LINK,
    boolean=["account_verified"],
    plural=["links", "expanded_links"],
    json=["media"],
)

CrowdTangleSummary = namedrecord("CrowdTangleSummary", CROWDTANGLE_SUMMARY_CSV_HEADERS)

CrowdTangleLeaderboard = namedrecord(
    "CrowdTangleLeaderboard", CROWDTANGLE_LEADERBOARD_CSV_HEADERS, boolean=["verified"]
)

CrowdTangleLeaderboardWithBreakdown = namedrecord(
    "CrowdTangleLeaderboardWithBreakdown",
    CROWDTANGLE_LEADERBOARD_CSV_HEADERS_WITH_BREAKDOWN,
    boolean=["verified"],
)

CrowdTangleList = namedrecord("CrowdTangleList", CROWDTANGLE_LIST_CSV_HEADERS)


def map_key(key, target):
    return [item[key] for item in target]


def format_post(post, link=None):
    row = [
        post["id"],
        post["platformId"],
        post["platform"],
        post["type"],
        post.get("title"),
        post.get("caption"),
        post.get("message"),
        post.get("description"),
        post["date"].split(" ", 1)[0],
        post["date"],
        post["updated"],
        post.get("link"),
        post.get("postUrl"),
        post["score"],
        post.get("videoLengthMS"),
        post.get("liveVideoStatus"),
    ]

    if link:
        row = [link] + row

    stats = post["statistics"]
    actual_stats = stats["actual"]
    expected_stats = stats["expected"]

    for name in CROWDTANGLE_STATISTICS:
        key = "%sCount" % name

        row.append(actual_stats.get(key, ""))
        row.append(expected_stats.get(key, ""))

    account = post["account"]

    row.extend(
        [
            # Account
            account["id"],
            account.get("platformId"),
            account.get("platform"),
            account["name"],
            account.get("handle"),
            account.get("profileImage"),
            account["subscriberCount"],
            account["url"],
            account["verified"],
            account.get("accountType"),
            account.get("pageAdminTopCountry"),
            # Remaining
            map_key("original", post.get("expandedLinks", [])),
            map_key("expanded", post.get("expandedLinks", [])),
            post.get("media"),
        ]
    )

    if link is not None:
        return CrowdTanglePostWithLink(*row)

    return CrowdTanglePost(*row)


def format_summary(stats):
    row = (stats["%sCount" % t] for t in CROWDTANGLE_REACTION_TYPES)
    return CrowdTangleSummary(*row)


def format_leaderboard(item, with_breakdown=False):
    account = item["account"]
    subscriber_data = item["subscriberData"]

    row = [
        account["id"],
        account["name"],
        account.get("handle"),
        account.get("profileImage"),
        account["subscriberCount"],
        account["url"],
        account["verified"],
        subscriber_data["initialCount"],
        subscriber_data["finalCount"],
        subscriber_data.get("notes"),
    ]

    summary = item["summary"]

    for key, _ in CROWDTANGLE_FULL_STATISTICS:
        row.append(summary.get(key))

    if with_breakdown:
        breakdown = item["breakdown"]

        for post_type in CROWDTANGLE_POST_TYPES:

            data = breakdown.get(post_type)

            for key, _ in CROWDTANGLE_FULL_STATISTICS:
                row.append(data.get(key) if data else None)

    if with_breakdown:
        return CrowdTangleLeaderboardWithBreakdown(*row)

    return CrowdTangleLeaderboard(*row)


def format_list(item):
    return CrowdTangleList(item["id"], item["title"], item["type"])
