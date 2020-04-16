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
    'thankful'
]

CROWDTANGLE_PARTITION_STRATEGIES = {
    'day'
}

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
    'account_verified'
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
