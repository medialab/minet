# =============================================================================
# Minet CrowdTangle CLI Defaults
# =============================================================================
#
# General constants used throughout the CrowdTangle actions.
#

CROWDTANGLE_DEFAULT_RATE_LIMIT = 6  # Number of hits per minute

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

CROWDTANGLE_PARTITION_STRATEGIES = {
    'day'
}
