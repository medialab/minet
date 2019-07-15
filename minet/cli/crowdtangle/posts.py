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

URL_TEMPLATE = 'https://api.crowdtangle.com/posts?count=100&sortBy=%(sort_by)s&token=%(token)s'
DEFAULT_WAIT_TIME = 10


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
    'message',
    'description',
    'date',
    'updated',
    'link',
    'post_url',
    'score'
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
        post['message'],
        post.get('description', ''),
        post['date'],
        post['updated'],
        post['link'],
        post['postUrl'],
        post['score']
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
        account['handle'],
        account['profileImage'],
        account['subscriberCount'],
        account['url'],
        '1' if account['verified'] else '',
        json.dumps(post['expandedLinks'], ensure_ascii=False),
        json.dumps(post['media'], ensure_ascii=False)
    ])

    return row


def print_error(*msg):
    print(*msg, file=sys.stderr)


def crowdtangle_posts_action(namespace, output_file):
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where(),
    )

    N = 0
    url = forge_posts_url(namespace)

    print_error('Using the following starting url:')
    print_error(url)
    print_error()

    # Loading bar
    loading_bar = tqdm(
        desc='Fetching posts',
        dynamic_ncols=True,
        unit=' posts'
    )

    if namespace.format == 'csv':
        writer = csv.writer(output_file)
        writer.writerow(CSV_HEADERS)

    while True:
        result = http.request('GET', url)

        if result.status == 401:
            loading_bar.close()

            print_error('Your API token is invalid.')
            print_error('Check that you indicated a valid one using the `--token` argument.')
            sys.exit(1)

        if result.status >= 400:
            loading_bar.close()

            print_error(result.data, result.status)
            sys.exit(1)

        try:
            data = json.loads(result.data)['result']
        except:
            loading_bar.close()
            print_error('Misformatted JSON result.')
            sys.exit(1)

        if 'posts' not in data or len(data['posts']) == 0:
            break

        posts = data['posts']
        enough_to_stop = False

        for post in posts:

            N += 1
            loading_bar.update()

            if namespace.format == 'jsonl':
                output_file.write(json.dumps(post, ensure_ascii=False) + '\n')
            else:
                writer.writerow(format_post_for_csv(post))

            if N >= namespace.limit:
                enough_to_stop = True
                break

        # NOTE: I wish I had labeled loops in python...
        if enough_to_stop:
            loading_bar.close()
            print_error('The indicated limit of posts was reached.')
            break

        # Pagination
        # NOTE: we could adjust the `count` GET param but I am lazy
        pagination = data['pagination']

        if 'nextPage' not in pagination:
            loading_bar.close()
            print_error('We reached the end of pagination.')
            break

        url = pagination['nextPage']

        # Waiting a bit to respect the 6 reqs/min limit
        time.sleep(DEFAULT_WAIT_TIME)

    loading_bar.close()
