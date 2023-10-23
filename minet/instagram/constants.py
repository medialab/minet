# =============================================================================
# Minet Instagram Constants
# =============================================================================
#
# General constants used throughout the Instagram functions.
#
from urllib3 import Timeout

INSTAGRAM_URL = "https://www.instagram.com"
INSTAGRAM_PUBLIC_API_DEFAULT_TIMEOUT = Timeout(connect=10, read=60 * 2)
INSTAGRAM_MEDIA_TYPE = {1: "GraphImage", 2: "GraphVideo", 8: "GraphSidecar"}
INSTAGRAM_DEFAULT_THROTTLE = 30.0
INSTAGRAM_MAX_RANDOM_ADDENDUM = 10.0
INSTAGRAM_NB_REQUEST_LITTLE_WAIT = 10
INSTAGRAM_DEFAULT_THROTTLE_LITTLE_WAIT = 300.0
INSTAGRAM_MAX_RANDOM_ADDENDUM_LITTLE_WAIT = 300.0
INSTAGRAM_NB_REQUEST_BIG_WAIT = 2900
INSTAGRAM_DEFAULT_THROTTLE_BIG_WAIT = 1800.0
INSTAGRAM_MAX_RANDOM_ADDENDUM_BIG_WAIT = 1800.0
INSTAGRAM_MIN_TIME_RETRYER = 600.0

INSTAGRAM_COMMENT_CSV_HEADERS = [
    "id",
    "index",
    "parent_id",
    "child_index",
    "text",
    "hashtags",
    "mentioned_names",
    "has_translation",
    "comment_like_count",
    "is_liked_by_media_owner",
    "child_comment_count",
    "created_at_utc",
    "utc_time",
    "username",
    "user_id",
    "user_full_name",
    "user_is_private",
    "user_is_mentionable",
    "user_is_verified",
    "user_profile_pic_id",
    "user_profile_pic_url",
    "user_fbid_v2",
]

INSTAGRAM_HASHTAG_POST_CSV_HEADERS = [
    "id",
    "media_type",
    "shortcode",
    "url",
    "caption",
    "hashtags",
    "mentioned_names",
    "liked_by_count",
    "comments_disabled",
    "comment_count",
    "preview_like_count",
    "video_view_count",
    "owner_id",
    "taken_at_timestamp",
    "utc_time",
    "accessibility_caption",
    "display_url",
]

INSTAGRAM_POST_CSV_HEADERS = [
    "username",
    "full_name",
    "is_verified",
    "id",
    "media_type",
    "shortcode",
    "url",
    "caption",
    "hashtags",
    "mentioned_names",
    "like_and_view_counts_disabled",
    "like_count",
    "comment_count",
    "main_thumbnail_url",
    "medias_type",
    "medias_url",
    "usertags_medias",
    "taken_at_timestamp",
    "utc_time",
    "coauthor_usernames",
]

INSTAGRAM_USER_CSV_HEADERS = [
    "id",
    "username",
    "full_name",
    "is_private",
    "profile_pic_url",
    "profile_pic_id",
    "is_verified",
    "has_anonymous_profile_picture",
    "has_highlight_reels",
    "account_badges",
    "similar_user_id",
    "latest_reel_media",
    "is_favorite",
]

INSTAGRAM_USER_INFO_CSV_HEADERS = [
    "username",
    "id",
    "full_name",
    "profile_pic_url_hd",
    "is_private",
    "is_verified",
    "biography",
    "bio_links_title",
    "bio_links_url",
    "biography_with_username",
    "biography_with_hashtag",
    "follower_count",
    "follow_count",
    "hide_like_and_view_counts",
    "pronouns",
    "has_ar_effects",
    "has_clips",
    "has_guides",
    "has_channel",
    "is_business_account",
    "is_professional_account",
    "is_supervision_enabled",
    "is_guardian_of_viewer",
    "is_supervised_by_viewer",
    "is_supervised_user",
    "guardian_id",
    "is_joined_recently",
    "business_category_name",
    "category_name",
    "connected_fb_page",
]
