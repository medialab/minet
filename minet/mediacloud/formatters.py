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
    MEDIACLOUD_STORIES_CSV_HEADER
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
