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

MEDIACLOUD_MEDIA_CSV_HEADER = [
    'media_id',
    'media_name',
    'media_url',
    'is_healthy',
    'is_monitored',
    'public_notes',
    'num_stories_90',
    'num_sentences_90',
    'start_date',
    'tags',
    'tag_sets',
    'tags_ids',
    'tag_sets_ids'
]

MEDIACLOUD_FEED_CSV_HEADER = [
    'name',
    'url',
    'feeds_id',
    'type',
    'media_id',
    'active',
    'last_attempted_download_time',
    'last_new_story_time',
    'last_successful_download_time'
]
