# =============================================================================
# Minet CrowdTangle Posts CLI Action
# =============================================================================
#
# Logic of the `ct posts` action.
#
from minet.cli.crowdtangle.utils import create_paginated_action
from minet.cli.crowdtangle.constants import CROWDTANGLE_POST_TYPES

URL_TEMPLATE = 'https://api.crowdtangle.com/leaderboard?count=100&token=%s'


def forge_leaderboard_url(namespace):
    base_url = URL_TEMPLATE % namespace.token

    if namespace.list_id:
        base_url += '&listId=%s' % namespace.list_id

    return base_url


CSV_HEADERS = [
    'ct_id',
    'name',
    'handle',
    'profile_image',
    'subscriber_count',
    'url',
    'verified',
    'initial_subscriber_count',
    'final_subscriber_count',
    'subscriber_data_notes'
]

STATISTICS = [
    ('loveCount', 'love_count'),
    ('wowCount', 'wow_count'),
    ('thankfulCount', 'thankful_count'),
    ('interactionRate', 'interaction_rate'),
    ('likeCount', 'like_count'),
    ('hahaCount', 'haha_count'),
    ('commentCount', 'comment_count'),
    ('shareCount', 'share_count'),
    ('sadCount', 'sad_count'),
    ('angryCount', 'angry_count'),
    ('postCount', 'post_count'),
    ('totalInteractionCount', 'total_interaction_count'),
    ('totalVideoTimeMS', 'total_video_time_ms'),
    ('threePlusMinuteVideoCount', 'three_plus_minute_video_count')
]

# Summary keys
for _, substitute_key in STATISTICS:
    CSV_HEADERS.append(substitute_key)


def build_csv_headers(namespace):
    basic_headers = list(CSV_HEADERS)

    if not namespace.breakdown:
        return basic_headers

    for post_type in CROWDTANGLE_POST_TYPES:
        for _, substitute_key in STATISTICS:
            basic_headers.append('%s_%s' % (post_type, substitute_key))

    return basic_headers


def format_account_for_csv(namespace, item):
    account = item['account']
    subscriber_data = item['subscriberData']

    row = [
        account['id'],
        account['name'],
        account.get('handle', ''),
        account['profileImage'],
        account['subscriberCount'],
        account['url'],
        '1' if account['verified'] else '',
        subscriber_data['initialCount'],
        subscriber_data['finalCount'],
        subscriber_data.get('notes', '')
    ]

    summary = item['summary']

    for key, _ in STATISTICS:
        row.append(summary.get(key, ''))

    if not namespace.breakdown:
        return row

    breakdown = item['breakdown']

    for post_type in CROWDTANGLE_POST_TYPES:

        data = breakdown.get(post_type)

        for key, _ in STATISTICS:
            row.append(data.get(key, '') if data else '')

    return row


crowdtangle_leaderboard_action = create_paginated_action(
    url_forge=forge_leaderboard_url,
    csv_headers=build_csv_headers,
    csv_formatter=format_account_for_csv,
    item_name='accounts',
    item_key='accountStatistics'
)
