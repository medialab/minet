# =============================================================================
# Minet CrowdTangle Constants
# =============================================================================
#
# General constants used throughout the CrowdTangle functions.
#
from urllib3 import Timeout

CROWDTANGLE_OUTPUT_FORMATS = {
    'raw',
    'csv_row',
    'csv_dict_row'
}

CROWDTANGLE_DEFAULT_RATE_LIMIT = 6  # Number of hits per minute
CROWDTANGLE_LINKS_DEFAULT_RATE_LIMIT = 2

CROWDTANGLE_DEFAULT_TIMEOUT = Timeout(connect=10, read=60 * 5)

CROWDTANGLE_POST_TYPES = [
    'episode',
    'extra_clip',
    'link',
    'live_video',
    'live_video_complete',
    'live_video_scheduled',
    'native_video',
    'photo',
    'status',
    'trailer',
    'tweet',
    'video',
    'vine',
    'youtube'
]

CROWDTANGLE_SORT_TYPES = [
    'date',
    'interaction_rate',
    'overperforming',
    'total_interactions',
    'underperforming'
]

CROWDTANGLE_SUMMARY_SORT_TYPES = {
    'date',
    'subscriber_count',
    'total_interactions'
}

CROWDTANGLE_SUMMARY_DEFAULT_SORT_TYPE = 'date'

CROWDTANGLE_SEARCH_FIELDS = {
    'text_fields_and_image_text',
    'include_query_strings',
    'text_fields_only',
    'account_name_only',
    'image_text_only'
}

CROWDTANGLE_DEFAULT_SEARCH_FIELD = 'text_fields_and_image_text'

CROWDTANGLE_STATISTICS = [
    'like',
    'share',
    'favorite',
    'comment',
    'love',
    'wow',
    'haha',
    'sad',
    'angry',
    'thankful',
    'care'
]

CROWDTANGLE_FULL_STATISTICS = STATISTICS = [
    ('loveCount', 'love_count'),
    ('wowCount', 'wow_count'),
    ('thankfulCount', 'thankful_count'),
    ('interactionRate', 'interaction_rate'),
    ('likeCount', 'like_count'),
    ('hahaCount', 'haha_count'),
    ('commentCount', 'comment_count'),
    ('shareCount', 'share_count'),
    ('sadCount', 'sad_count'),
    ('angryCount', 'angry_count'),
    ('postCount', 'post_count'),
    ('totalInteractionCount', 'total_interaction_count'),
    ('totalVideoTimeMS', 'total_video_time_ms'),
    ('threePlusMinuteVideoCount', 'three_plus_minute_video_count')
]

CROWDTANGLE_PLATFORMS = {
    'facebook',
    'instagram',
    'reddit'
}

CROWDTANGLE_REACTION_TYPES = [
    'angry',
    'comment',
    'haha',
    'like',
    'love',
    'sad',
    'share',
    'thankful',
    'wow'
]

CROWDTANGLE_POST_CSV_HEADERS = [
    'ct_id',
    'id',
    'platform',
    'type',
    'title',
    'caption',
    'message',
    'description',
    'date',
    'datetime',
    'updated',
    'link',
    'post_url',
    'score',
    'video_length_ms',
    'live_video_status'
]

for name in CROWDTANGLE_STATISTICS:
    CROWDTANGLE_POST_CSV_HEADERS.append('actual_%s_count' % name)
    CROWDTANGLE_POST_CSV_HEADERS.append('expected_%s_count' % name)

CROWDTANGLE_ACCOUNT_CSV_HEADERS = [
    'account_ct_id',
    'account_id',
    'account_platform',
    'account_name',
    'account_handle',
    'account_profile_image',
    'account_subscriber_count',
    'account_url',
    'account_verified',
    'account_platform',
    'account_type',
    'account_page_admin_top_country'
]

CROWDTANGLE_MEDIA_CSV_HEADERS = [
    'links',
    'expanded_links',
    'media'
]

CROWDTANGLE_POST_CSV_HEADERS += CROWDTANGLE_ACCOUNT_CSV_HEADERS
CROWDTANGLE_POST_CSV_HEADERS += CROWDTANGLE_MEDIA_CSV_HEADERS

CROWDTANGLE_POST_CSV_HEADERS_WITH_LINK = ['url'] + CROWDTANGLE_POST_CSV_HEADERS

CROWDTANGLE_SUMMARY_CSV_HEADERS = ['%s_count' % t for t in CROWDTANGLE_REACTION_TYPES]

CROWDTANGLE_LEADERBOARD_CSV_HEADERS = [
    'ct_id',
    'name',
    'handle',
    'profile_image',
    'subscriber_count',
    'url',
    'verified',
    'initial_subscriber_count',
    'final_subscriber_count',
    'subscriber_data_notes'
]

for _, substitute_key in CROWDTANGLE_FULL_STATISTICS:
    CROWDTANGLE_LEADERBOARD_CSV_HEADERS.append(substitute_key)

CROWDTANGLE_LEADERBOARD_CSV_HEADERS_WITH_BREAKDOWN = list(CROWDTANGLE_LEADERBOARD_CSV_HEADERS)

for post_type in CROWDTANGLE_POST_TYPES:
    for _, substitute_key in CROWDTANGLE_FULL_STATISTICS:
        CROWDTANGLE_LEADERBOARD_CSV_HEADERS_WITH_BREAKDOWN.append('%s_%s' % (post_type, substitute_key))

CROWDTANGLE_LIST_CSV_HEADERS = [
    'id',
    'title',
    'type'
]
