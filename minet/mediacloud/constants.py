# =============================================================================
# Minet Mediacloud Constants
# =============================================================================
#
# Bunch of mediacloud-related constants.
#
from urllib3 import Timeout


MEDIACLOUD_API_BASE_URL = 'https://api.mediacloud.org/api/v2'
MEDIACLOUD_DEFAULT_TIMEOUT = Timeout(connect=30, read=60 * 5)
MEDIACLOUD_DEFAULT_BATCH = 250

MEDIACLOUD_TOPIC_STORIES_CSV_HEADERS = [
    'guid',
    'stories_id',
    'title',
    'url',
    'language',
    'media_id',
    'media_name',
    'collect_date',
    'publish_date',
    'date_is_reliable',
    'facebook_share_count',
    'full_text_rss',
    'inlink_count',
    'outlink_count',
    'media_inlink_count',
    'post_count',
    'snapshots_id',
    'timespans_id',
    'next_link_id'
]

MEDIACLOUD_STORIES_CSV_HEADER = [
    'guid',
    'stories_id',
    'processed_stories_id',
    'title',
    'url',
    'language',
    'collect_date',
    'publish_date',
    'media_id',
    'media_name',
    'media_url',
    'tags',
    'tag_sets',
    'tags_ids',
    'tag_sets_ids'
]
