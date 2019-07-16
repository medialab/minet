# =============================================================================
# Minet CrowdTangle CLI Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the CrowdTangle actions.
#
import csv
import sys
import json
import time
import urllib3
import certifi
from tqdm import tqdm

from minet.cli.utils import print_err
from minet.cli.crowdtangle.defaults import CROWDTANGLE_DEFAULT_WAIT_TIME


def create_paginated_action(url_forge, csv_headers, csv_formatter,
                            item_name, item_key):

    def action(namespace, output_file):
        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where(),
        )

        N = 0
        url = url_forge(namespace)

        print_err('Using the following starting url:')
        print_err(url)
        print_err()

        # Loading bar
        loading_bar = tqdm(
            desc='Fetching %s' % item_name,
            dynamic_ncols=True,
            unit=' %s' % item_name
        )

        if namespace.format == 'csv':
            writer = csv.writer(output_file)
            writer.writerow(csv_headers(namespace))

        while True:
            result = http.request('GET', url)

            if result.status == 401:
                loading_bar.close()

                print_err('Your API token is invalid.')
                print_err('Check that you indicated a valid one using the `--token` argument.')
                sys.exit(1)

            if result.status >= 400:
                loading_bar.close()

                print_err(result.data, result.status)
                sys.exit(1)

            try:
                data = json.loads(result.data)['result']
            except:
                loading_bar.close()
                print_err('Misformatted JSON result.')
                sys.exit(1)

            if item_key not in data or len(data[item_key]) == 0:
                break

            items = data[item_key]
            enough_to_stop = False

            for item in items:
                N += 1
                loading_bar.update()

                if namespace.format == 'jsonl':
                    output_file.write(json.dumps(item, ensure_ascii=False) + '\n')
                else:
                    writer.writerow(csv_formatter(namespace, item))

                if N >= namespace.limit:
                    enough_to_stop = True
                    break

            # NOTE: I wish I had labeled loops in python...
            if enough_to_stop:
                loading_bar.close()
                print_err('The indicated limit of %s was reached.' % item_name)
                break

            # Pagination
            # NOTE: we could adjust the `count` GET param but I am lazy
            pagination = data['pagination']

            if 'nextPage' not in pagination:
                loading_bar.close()
                print_err('We reached the end of pagination.')
                break

            url = pagination['nextPage']

            # Waiting a bit to respect the 6 reqs/min limit
            time.sleep(CROWDTANGLE_DEFAULT_WAIT_TIME)

        loading_bar.close()


    return action
