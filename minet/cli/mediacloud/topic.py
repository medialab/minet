# =============================================================================
# Minet Mediacloud Topic CLI Action
# =============================================================================
#
# Logic of the `mc topic` action.
#
import csv
import json
from tqdm import tqdm
from urllib3 import Timeout

from minet.cli.mediacloud.constants import MEDIACLOUD_API_BASE_URL
from minet.utils import create_pool, request
from minet.cli.utils import print_err


def forge_url(namespace, link_id=None):
    url = '%s/topics/%s/stories/list?key=%s&limit=250' % (
        MEDIACLOUD_API_BASE_URL,
        namespace.topic_id,
        namespace.token
    )

    if link_id is not None:
        url += '&link_id=%s' % link_id

    return url


def get(http, url):
    error, response = request(http, url)

    if error:
        return error, None

    data = json.loads(response.data.decode())

    return None, data


OUPUT_HEADERS = [
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


def format_csv_row(item, next_link_id):
    return [
        item['guid'],
        item['stories_id'],
        item['title'],
        item['url'],
        item['language'],
        item['media_id'],
        item['media_name'],
        item['collect_date'],
        item['publish_date'],
        item['date_is_reliable'],
        item['facebook_share_count'],
        '1' if item['full_text_rss'] else '0',
        item['inlink_count'],
        item['outlink_count'],
        item['media_inlink_count'],
        item['post_count'] or '',
        item['snapshots_id'],
        item['timespans_id'],
        next_link_id or ''
    ]


def get_next_link_id(data):

    if 'link_ids' not in data:
        return None

    pagination = data['link_ids']

    if not pagination.get('next'):
        return None

    return pagination['next']


def mediacloud_topic_action(namespace, output_file):
    link_id = None

    writer = csv.writer(output_file)
    writer.writerow(OUPUT_HEADERS)

    http = create_pool(timeout=Timeout(connect=30, read=60 * 5))

    print_err('Using the following starting url:')
    print_err(forge_url(namespace, link_id))
    print_err()

    loading_bar = tqdm(
        desc='Fetching stories',
        dynamic_ncols=True,
        unit=' stories'
    )

    while True:
        error, data = get(http, forge_url(namespace, link_id))

        if error:
            raise error

        if 'stories' not in data or len(data['stories']) == 0:
            break

        next_link_id = get_next_link_id(data)

        for story in data['stories']:
            writer.writerow(format_csv_row(story, next_link_id))

        loading_bar.update(len(data['stories']))

        if next_link_id is None:
            break

        link_id = next_link_id
