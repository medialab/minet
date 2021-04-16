# =============================================================================
# Minet Mediacloud Formatters
# =============================================================================
#
# Miscellaneous mediacloud-related formatter functions.
#
from casanova import namedrecord

from minet.mediacloud.utils import explode_tags
from minet.mediacloud.constants import (
    MEDIACLOUD_TOPIC_STORIES_CSV_HEADERS,
    MEDIACLOUD_STORIES_CSV_HEADER,
    MEDIACLOUD_MEDIA_CSV_HEADER,
    MEDIACLOUD_FEED_CSV_HEADER
)

MediacloudTopicStory = namedrecord(
    'MediacloudTopicStory',
    MEDIACLOUD_TOPIC_STORIES_CSV_HEADERS,
    boolean=['full_text_rss']
)

MediacloudStory = namedrecord(
    'MediacloudStory',
    MEDIACLOUD_STORIES_CSV_HEADER,
    plural=[
        'tags',
        'tag_sets',
        'tags_ids',
        'tag_sets_ids'
    ]
)

MediacloudMedia = namedrecord(
    'MediacloudMedia',
    MEDIACLOUD_MEDIA_CSV_HEADER,
    boolean=['is_healthy', 'is_monitored'],
    plural=[
        'tags',
        'tag_sets',
        'tags_ids',
        'tag_sets_ids'
    ]
)

MediacloudFeed = namedrecord(
    'MediacloudFeed',
    MEDIACLOUD_FEED_CSV_HEADER,
    boolean=['active']
)


def format_topic_story(story, next_link_id=None):
    return MediacloudTopicStory(
        story['guid'],
        story['stories_id'],
        story['title'],
        story['url'],
        story['language'],
        story['media_id'],
        story['media_name'],
        story['collect_date'],
        story['publish_date'],
        story['date_is_reliable'],
        story['facebook_share_count'],
        bool(story['full_text_rss']),
        story['inlink_count'],
        story['outlink_count'],
        story['media_inlink_count'],
        story['post_count'],
        story['snapshots_id'],
        story['timespans_id'],
        next_link_id
    )


def format_story(story, as_dict=False):
    tags = story.get('story_tags')

    return MediacloudStory(
        story['guid'],
        story['stories_id'],
        story['processed_stories_id'],
        story['title'],
        story['url'],
        story['language'],
        story['collect_date'],
        story['publish_date'],
        story['media_id'],
        story['media_name'],
        story['media_url'],
        *explode_tags(tags)
    )


def format_media(media, as_dict=False):
    tags = media.get('media_source_tags')

    return MediacloudMedia(
        media['media_id'],
        media['name'],
        media['url'],
        media['is_healthy'],
        media['is_monitored'],
        media.get('public_notes'),
        media['num_stories_90'],
        media['num_sentences_90'],
        media['start_date'],
        *explode_tags(tags)
    )


def format_feed(feed, as_dict=False):
    return MediacloudFeed(
        feed['name'],
        feed['url'],
        feed['feeds_id'],
        feed['type'],
        feed['media_id'],
        feed['active'],
        feed.get('last_attempted_download_time'),
        feed.get('last_new_story_time'),
        feed.get('last_successful_download_time')
    )
