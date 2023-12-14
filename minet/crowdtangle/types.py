from typing import Optional, List, Any

from dataclasses import dataclass
from casanova import TabularRecord, tabular_field

from minet.crowdtangle.constants import (
    CROWDTANGLE_STATISTICS,
    CROWDTANGLE_REACTION_TYPES,
    CROWDTANGLE_FULL_STATISTICS,
)


@dataclass
class CrowdTangleAccount(TabularRecord):
    ct_id: str
    id: str
    platform: str
    name: str
    handle: Optional[str]
    profile_image: str
    subscriber_count: int
    url: str
    verified: bool
    type: str
    page_admin_top_country: Optional[str]


def map_key(key, target):
    return [item[key] for item in target]


@dataclass
class CrowdTanglePost(TabularRecord):
    ct_id: str
    id: str
    platform: str
    type: str
    title: Optional[str]
    caption: Optional[str]
    message: Optional[str]
    description: Optional[str]
    date: str
    datetime: str
    updated: str
    link: str
    post_url: str
    score: float
    video_length_ms: str
    live_video_status: str
    actual_like_count: int
    expected_like_count: int
    actual_share_count: int
    expected_share_count: int
    actual_favorite_count: int
    expected_favorite_count: int
    actual_comment_count: int
    expected_comment_count: int
    actual_love_count: int
    expected_love_count: int
    actual_wow_count: int
    expected_wow_count: int
    actual_haha_count: int
    expected_haha_count: int
    actual_sad_count: int
    expected_sad_count: int
    actual_angry_count: int
    expected_angry_count: int
    actual_thankful_count: int
    expected_thankful_count: int
    actual_care_count: int
    expected_care_count: int
    account: CrowdTangleAccount
    links: List[str]
    expanded_links: List[str]
    media: Any = tabular_field(as_json=True)

    @classmethod
    def from_payload(cls, payload) -> "CrowdTanglePost":
        row = [
            payload["id"],
            payload["platformId"],
            payload["platform"],
            payload["type"],
            payload.get("title"),
            payload.get("caption"),
            payload.get("message"),
            payload.get("description"),
            payload["date"].split(" ", 1)[0],
            payload["date"],
            payload["updated"],
            payload.get("link"),
            payload.get("postUrl"),
            payload["score"],
            payload.get("videoLengthMS"),
            payload.get("liveVideoStatus"),
        ]

        stats = payload["statistics"]
        actual_stats = stats["actual"]
        expected_stats = stats["expected"]

        for name in CROWDTANGLE_STATISTICS:
            key = "%sCount" % name

            row.append(actual_stats.get(key, ""))
            row.append(expected_stats.get(key, ""))

        account = payload["account"]
        account = CrowdTangleAccount(
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
        )

        row.extend(
            [
                # Account
                account,
                # Remaining
                map_key("original", payload.get("expandedLinks", [])),
                map_key("expanded", payload.get("expandedLinks", [])),
                payload.get("media"),
            ]
        )

        return cls(*row)


@dataclass
class CrowdTangleSummary(TabularRecord):
    angry_count: int
    comment_count: int
    haha_count: int
    like_count: int
    love_count: int
    sad_count: int
    share_count: int
    thankful_count: int
    wow_count: int

    @classmethod
    def from_payload(cls, payload) -> "CrowdTangleSummary":
        row = (payload["%sCount" % t] for t in CROWDTANGLE_REACTION_TYPES)
        return cls(*row)


@dataclass
class CrowdTangleLeaderboard(TabularRecord):
    ct_id: str
    name: str
    handle: str
    profile_image: str
    subscriber_count: int
    url: str
    verified: bool
    initial_subscriber_count: int
    final_subscriber_count: int
    subscriber_data_notes: str
    love_count: int
    wow_count: int
    thankful_count: int
    interaction_rate: int
    like_count: int
    haha_count: int
    comment_count: int
    share_count: int
    sad_count: int
    angry_count: int
    post_count: int
    total_interaction_count: int
    total_video_time_ms: int
    three_plus_minute_video_count: int

    @classmethod
    def from_payload(cls, payload) -> "CrowdTangleLeaderboard":
        account = payload["account"]
        subscriber_data = payload["subscriberData"]

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

        summary = payload["summary"]

        for key, _ in CROWDTANGLE_FULL_STATISTICS:
            row.append(summary.get(key))

        return cls(*row)


@dataclass
class CrowdTangleList(TabularRecord):
    id: str
    title: str
    type: str

    @classmethod
    def from_payload(cls, payload) -> "CrowdTangleList":
        return cls(payload["id"], payload["title"], payload["type"])
