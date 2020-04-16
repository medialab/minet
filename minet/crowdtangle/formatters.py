# =============================================================================
# Minet CrowdTangle Formatters
# =============================================================================
#
# Various data formatters for CrowdTangle API data.
#
import json
from collections import OrderedDict

from minet.crowdtangle.constants import (
    CROWDTANGLE_POST_CSV_HEADERS,
    CROWDTANGLE_POST_CSV_HEADERS_WITH_LINK,
    CROWDTANGLE_SUMMARY_CSV_HEADERS,
    CROWDTANGLE_STATISTICS
)


def row_to_ordered_dict(headers, row):
    return OrderedDict(zip(headers, row))


def format_post(post, as_dict=False, link=None):
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

    if link:
        row = [link] + row

    stats = post['statistics']
    actual_stats = stats['actual']
    expected_stats = stats['expected']

    for name in CROWDTANGLE_STATISTICS:
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

    if as_dict:
        headers = CROWDTANGLE_POST_CSV_HEADERS

        if link is not None:
            headers = CROWDTANGLE_POST_CSV_HEADERS_WITH_LINK

        return row_to_ordered_dict(headers, row)

    return row


def format_summary(stats, as_dict=False):
    row = [stats['%sCount' % t] for t in CROWDTANGLE_REACTION_TYPES]

    if as_dict:
        return row_to_ordered_dict(CROWDTANGLE_SUMMARY_CSV_HEADERS)

    return row
