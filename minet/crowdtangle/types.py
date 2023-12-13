from typing import Optional, List, Any

from dataclasses import dataclass
from casanova import TabularRecord, tabular_field

# TODO: the conversion was pretty lazy...


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
    page_admin_top_country: str


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


@dataclass
class CrowdTangleSummary(TabularRecord):
    pass


@dataclass
class CrowdTangleLeaderboard(TabularRecord):
    pass


@dataclass
class CrowdTangleLeaderboardWithBreakdown(TabularRecord):
    pass


@dataclass
class CrowdTangleList(TabularRecord):
    pass
