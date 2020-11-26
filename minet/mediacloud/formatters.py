# =============================================================================
# Minet Mediacloud Formatters
# =============================================================================
#
# Miscellaneous mediacloud-related formatter functions.
#
from collections import OrderedDict

from minet.mediacloud.utils import explode_tags
from minet.mediacloud.constants import (
    MEDIACLOUD_TOPIC_STORIES_CSV_HEADERS,
    MEDIACLOUD_STORIES_CSV_HEADER,
    MEDIACLOUD_MEDIA_CSV_HEADER,
    MEDIACLOUD_FEED_CSV_HEADER
)


def row_to_ordered_dict(headers, row):
    return OrderedDict(zip(headers, row))


def format_topic_story(story, next_link_id, as_dict=False):
    row = [
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
        '1' if story['full_text_rss'] else '0',
        story['inlink_count'],
        story['outlink_count'],
        story['media_inlink_count'],
        story['post_count'] or '',
        story['snapshots_id'],
        story['timespans_id'],
        next_link_id or ''
    ]

    if as_dict:
        row = row_to_ordered_dict(MEDIACLOUD_TOPIC_STORIES_CSV_HEADERS, row)

    return row


TAGS_PADDING = [''] * 4


def format_story(story, as_dict=False):
    tags = story.get('story_tags')

    row = [
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
        *(explode_tags(tags, join_char='|') if tags else TAGS_PADDING)
    ]

    if as_dict:
        row = row_to_ordered_dict(MEDIACLOUD_STORIES_CSV_HEADER, row)

    return row


def format_media(media, as_dict=False):
    tags = media.get('media_source_tags')

    row = [
        media['media_id'],
        media['name'],
        media['url'],
        'true' if media['is_healthy'] else 'false',
        'true' if media['is_monitored'] else 'false',
        media.get('public_notes', ''),
        media['num_stories_90'],
        media['num_sentences_90'],
        media['start_date'],
        *(explode_tags(tags, join_char='|') if tags else TAGS_PADDING)
    ]

    if as_dict:
        row = row_to_ordered_dict(MEDIACLOUD_MEDIA_CSV_HEADER, row)

    return row


def format_feed(feed, as_dict=False):
    row = [
        feed['name'],
        feed['url'],
        feed['feeds_id'],
        feed['type'],
        feed['media_id'],
        'true' if feed['active'] else 'false',
        feed.get('last_attempted_download_time', ''),
        feed.get('last_new_story_time', ''),
        feed.get('last_successful_download_time', '')
    ]

    if as_dict:
        row = row_to_ordered_dict(MEDIACLOUD_FEED_CSV_HEADER, row)

    return row
