# =============================================================================
# Minet CrowdTangle Posts CLI Action
# =============================================================================
#
# Logic of the `ct posts` action.
#
import csv
import sys
import json
import time
import urllib3
import certifi
from tqdm import tqdm

from minet.cli.utils import print_err
from minet.cli.crowdtangle.utils import create_paginated_action

URL_TEMPLATE = 'https://api.crowdtangle.com/posts?count=100&sortBy=%(sort_by)s&token=%(token)s'


def forge_posts_url(namespace):
    base_url = URL_TEMPLATE % {
        'sort_by': namespace.sort_by,
        'token': namespace.token
    }

    if namespace.language:
        base_url += '&language=%s' % namespace.language

    if namespace.start_date:
        base_url += '&startDate=%s' % namespace.start_date

    if namespace.end_date:
        base_url += '&endDate=%s' % namespace.end_date

    if namespace.list_ids:
        base_url += '&list-ids=%s' % namespace.list_ids

    return base_url

CSV_HEADERS = [
    'ct_id',
    'fb_id',
    'type',
    'title',
    'caption',
    'message',
    'description',
    'date',
    'updated',
    'link',
    'post_url',
    'score',
    'video_length_ms',
    'live_video_status'
]

STATISTICS = [
    'like',
    'share',
    'comment',
    'love',
    'wow',
    'haha',
    'sad',
    'angry',
    'thankful'
]

for name in STATISTICS:
    CSV_HEADERS.append('actual_%s_count' % name)
    CSV_HEADERS.append('expected_%s_count' % name)

CSV_HEADERS = CSV_HEADERS + [
    'account_ct_id',
    'account_fb_id',
    'account_name',
    'account_handle',
    'account_profile_image',
    'account_subscriber_count',
    'account_url',
    'account_verified',
    'expanded_links',
    'media'
]


def format_post_for_csv(post):
    row = [
        post['id'],
        post['platformId'],
        post['type'],
        post.get('title', ''),
        post.get('caption', ''),
        post.get('message', ''),
        post.get('description', ''),
        post['date'],
        post['updated'],
        post.get('link', ''),
        post['postUrl'],
        post['score'],
        post.get('videoLengthMS', ''),
        post.get('liveVideoStatus', '')
    ]

    stats = post['statistics']
    actual_stats = stats['actual']
    expected_stats = stats['expected']

    for name in STATISTICS:
        key = '%sCount' % name

        row.append(actual_stats[key])
        row.append(expected_stats[key])

    account = post['account']

    row.extend([
        account['id'],
        account['platformId'],
        account['name'],
        account.get('handle', ''),
        account['profileImage'],
        account['subscriberCount'],
        account['url'],
        '1' if account['verified'] else '',
        json.dumps(post['expandedLinks'], ensure_ascii=False) if 'expandedLinks' in post else '',
        json.dumps(post['media'], ensure_ascii=False) if 'media' in post else ''
    ])

    return row

crowdtangle_posts_action = create_paginated_action(
    url_forge=forge_posts_url,
    csv_headers=CSV_HEADERS,
    csv_formatter=format_post_for_csv,
    item_name='posts',
    item_key='posts'
)
