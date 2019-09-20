# =============================================================================
# Minet CrowdTangle CLI Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the CrowdTangle actions.
#
import csv
import json
from datetime import date, timedelta
from tqdm import tqdm
from ural import get_domain_name, normalize_url
from urllib3 import Timeout

from minet.utils import create_safe_pool, fetch, RateLimiter
from minet.cli.utils import print_err, die
from minet.cli.crowdtangle.constants import CROWDTANGLE_DEFAULT_RATE_LIMIT

DAY_DELTA = timedelta(days=1)

URL_REPORT_HEADERS = [
    'post_ct_id',
    'post_id',
    'account_ct_id',
    'account_name',
    'account_handle',
    'original_url',
    'url',
    'normalized_url',
    'domain_name'
]


def format_url_for_csv(url_item, post):
    account = post['account']

    url = url_item['expanded']

    return [
        post['id'],
        post.get('platformId', ''),
        account['id'],
        account['name'],
        account.get('handle', ''),
        url_item['original'],
        url,
        normalize_url(url, strip_trailing_slash=True),
        get_domain_name(url)
    ]


def day_range(end):
    day_delta = timedelta(days=1)

    start_date = date(*[int(i) for i in end.split('-')])
    current_date = date.today()

    while start_date != current_date:
        end_date = current_date
        current_date -= day_delta

        yield current_date.isoformat(), end_date.isoformat()


class PartitionStrategyNoop(object):
    def __init__(self, namespace, url_forge):
        self.namespace = namespace
        self.url_forge = url_forge
        self.started = False

    def __call__(self, items):
        if not self.started:
            self.started = True
            return self.url_forge(self.namespace)

        return None

    def get_postfix(self):
        return None


class PartitionStrategyDay(object):
    def __init__(self, namespace, url_forge):
        self.namespace = namespace
        self.url_forge = url_forge

        self.range = day_range(namespace.start_date)

    def __call__(self, items):
        start_date, end_date = next(self.range, (None, None))

        if start_date is None:
            return None

        self.namespace.start_date = start_date
        self.namespace.end_date = end_date

        return self.url_forge(self.namespace)

    def get_postfix(self):
        return {'day': self.namespace.start_date}


PARTITION_STRATEGIES = {
    'day': PartitionStrategyDay
}


def step(http, url, item_key):
    err, result = fetch(http, url)

    # Debug
    if err:
        return 'http-error', err, None

    # Bad auth
    if result.status == 401:
        return 'bad-auth', None, None

    # Bad params
    if result.status >= 400:
        return 'bad-params', result, None

    try:
        data = json.loads(result.data)['result']
    except:
        return 'bad-json', None, None

    if item_key not in data or len(data[item_key]) == 0:
        return 'exhausted', None, None

    # Extracting next link
    pagination = data['pagination']
    meta = pagination['nextPage'] if 'nextPage' in pagination else None

    return 'ok', meta, data[item_key]


def create_paginated_action(url_forge, csv_headers, csv_formatter,
                            item_name, item_key):

    def action(namespace, output_file):
        http = create_safe_pool(timeout=Timeout(connect=10, read=60 * 5))

        url_report_writer = None

        if getattr(namespace, 'url_report', False):
            url_report_writer = csv.writer(namespace.url_report)
            url_report_writer.writerow(URL_REPORT_HEADERS)

        if getattr(namespace, 'partition_strategy', None):
            if isinstance(namespace.partition_strategy, int):
                pass
            else:

                if namespace.partition_strategy == 'day' and not namespace.start_date:
                    die('"--partition-strategy day" requires a "--start-date".')

                partition_strategy = PARTITION_STRATEGIES[namespace.partition_strategy](namespace, url_forge)
        else:
            partition_strategy = PartitionStrategyNoop(namespace, url_forge)

        N = 0
        C = 0
        url = partition_strategy(None)

        has_limit = bool(namespace.limit)

        print_err('Using the following starting url:')
        print_err(url)
        print_err()

        # Loading bar
        loading_bar = tqdm(
            desc='Fetching %s' % item_name,
            dynamic_ncols=True,
            unit=' %s' % item_name,
            total=namespace.limit
        )

        def set_postfix():
            postfix = {'calls': C}

            addendum = partition_strategy.get_postfix()

            if addendum is not None:
                postfix.update(addendum)

            loading_bar.set_postfix(**postfix)

        set_postfix()

        if namespace.format == 'csv':
            writer = csv.writer(output_file)
            writer.writerow(csv_headers(namespace) if callable(csv_headers) else csv_headers)

        rate_limit = namespace.rate_limit if namespace.rate_limit else CROWDTANGLE_DEFAULT_RATE_LIMIT
        rate_limiter = RateLimiter(rate_limit, 60.0)

        while url is not None:
            with rate_limiter:
                status, meta, items = step(http, url, item_key)
                C += 1

                # Debug
                if status == 'http-error':
                    loading_bar.close()
                    print_err(url)
                    raise meta

                if status == 'bad-auth':
                    loading_bar.close()
                    die([
                        'Your API token is invalid.',
                        'Check that you indicated a valid one using the `--token` argument.'
                    ])

                if status == 'bad-params':
                    loading_bar.close()
                    die([result.data, result.status])

                if status == 'bad-json':
                    loading_bar.close()
                    die('Misformatted JSON result.')

                if status == 'exhausted':
                    url = partition_strategy(None)
                    continue

                enough_to_stop = False
                next_url = meta

                set_postfix()

                for item in items:
                    N += 1

                    # TODO: could be done with the count instead
                    loading_bar.update()

                    if namespace.format == 'jsonl':
                        output_file.write(json.dumps(item, ensure_ascii=False) + '\n')
                    else:
                        writer.writerow(csv_formatter(namespace, item))

                    if url_report_writer:
                        urls = item.get('expandedLinks')

                        if urls:
                            for url_item in urls:
                                url_report_writer.writerow(format_url_for_csv(url_item, item))

                    if has_limit and N >= namespace.limit:
                        enough_to_stop = True
                        break

                # NOTE: I wish I had labeled loops in python...
                if enough_to_stop:
                    loading_bar.close()
                    print_err('The indicated limit of %s was reached.' % item_name)
                    break

                # Paginating
                if next_url is None:
                    if partition_strategy is None:
                        break

                    url = partition_strategy(items)
                    continue

                url = next_url

        loading_bar.close()

    return action
