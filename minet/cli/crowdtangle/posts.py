# =============================================================================
# Minet CrowdTangle Posts CLI Action
# =============================================================================
#
# Logic of the `ct posts` action.
#
import json

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
        base_url += '&listIds=%s' % namespace.list_ids

    return base_url


CSV_HEADERS = [
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

STATISTICS = [
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

for name in STATISTICS:
    CSV_HEADERS.append('actual_%s_count' % name)
    CSV_HEADERS.append('expected_%s_count' % name)

CSV_HEADERS = CSV_HEADERS + [
    'account_ct_id',
    'account_id',
    'account_platform',
    'account_name',
    'account_handle',
    'account_profile_image',
    'account_subscriber_count',
    'account_url',
    'account_verified',
    'links',
    'expanded_links',
    'media'
]


def format_post_for_csv(namespace, post):
    row = [
        post['id'],
        post['platformId'],
        post['platform'],
        post['type'],
        post.get('title', ''),
        post.get('caption', ''),
        post.get('message', ''),
        post.get('description', ''),
        post['date'].split(' ', 1)[0],
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

        row.append(actual_stats.get(key, ''))
        row.append(expected_stats.get(key, ''))

    account = post['account']

    links = ''
    expanded_links = ''

    if 'expandedLinks' in post:
        links = '|'.join(link['original'] for link in post['expandedLinks'])
        expanded_links = '|'.join(link['expanded'] for link in post['expandedLinks'])

    row.extend([
        account['id'],
        account.get('platformId', ''),
        account['platform'],
        account['name'],
        account.get('handle', ''),
        account['profileImage'],
        account['subscriberCount'],
        account['url'],
        '1' if account['verified'] else '',
        links,
        expanded_links,
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
