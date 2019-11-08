# =============================================================================
# Minet CrowdTangle CLI Defaults
# =============================================================================
#
# General constants used throughout the CrowdTangle actions.
#
from urllib3 import Timeout

CROWDTANGLE_DEFAULT_RATE_LIMIT = 6  # Number of hits per minute
CROWDTANTLE_LINKS_DEFAULT_RATE_LIMIT = 2

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
