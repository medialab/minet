# =============================================================================
# Minet CrowdTangle Posts CLI Action
# =============================================================================
#
# Logic of the `ct posts` action.
#
import sys
import json
import time
import urllib3
import certifi
from tqdm import tqdm

URL_TEMPLATE = 'https://api.crowdtangle.com/posts?count=100&sortBy=date&token=%s'
DEFAULT_WAIT_TIME = 10


def forge_posts_url(token):
    return URL_TEMPLATE % token


def print_error(*msg):
    print(*msg, file=sys.stderr)


def crowdtangle_posts_action(namespace, output_file):
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where(),
    )

    # Loading bar
    loading_bar = tqdm(
        desc='Fetching posts',
        dynamic_ncols=True,
        unit=' posts'
    )

    N = 0
    url = forge_posts_url(namespace.token)

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
