# =============================================================================
# Minet CrowdTangle CLI Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the CrowdTangle actions.
#
import csv
import casanova
import ndjson
from tqdm import tqdm

from minet.cli.utils import print_err, die
from minet.crowdtangle import CrowdTangleClient
from minet.crowdtangle.exceptions import (
    CrowdTangleInvalidTokenError
)


def make_paginated_action(method_name, item_name, csv_headers, get_args=None,
                          announce=None):

    def action(namespace, output_file):

        # Do we need to resume?
        need_to_resume = False

        if getattr(namespace, 'resume', False):
            need_to_resume = True

            if namespace.output is None:
                die(
                    'Cannot --resume without knowing the output (use -o/--output rather stdout).',
                )

            if namespace.sort_by != 'date':
                die('Cannot --resume if --sort_by is not `date`.')

            if namespace.format != 'csv':
                die('Cannot --resume jsonl format yet.')

            with open(namespace.output, 'r') as f:
                resume_reader = casanova.reader(f)

                last_cell = None
                resume_loader = tqdm(desc='Resuming', unit=' lines')

                for cell in resume_reader.cells('datetime'):
                    resume_loader.update()
                    last_cell = cell

                resume_loader.close()

                if last_cell is not None:
                    last_date = last_cell.replace(' ', 'T')
                    namespace.end_date = last_date

                    print_err('Resuming from: %s' % last_date)

        if callable(announce):
            print_err(announce(namespace))

        # Loading bar
        loading_bar = tqdm(
            desc='Fetching %s' % item_name,
            dynamic_ncols=True,
            unit=' %s' % item_name,
            total=namespace.limit
        )

        if namespace.format == 'csv':
            writer = csv.writer(output_file)

            if not need_to_resume:
                writer.writerow(csv_headers(namespace) if callable(csv_headers) else csv_headers)
        else:
            writer = ndjson.writer(output_file)

        client = CrowdTangleClient(namespace.token, rate_limit=namespace.rate_limit)

        args = []

        if callable(get_args):
            args = get_args(namespace)

        create_iterator = getattr(client, method_name)
        iterator = create_iterator(
            *args,
            partition_strategy=getattr(namespace, 'partition_strategy', None),
            limit=namespace.limit,
            format='csv_row' if namespace.format == 'csv' else 'raw',
            per_call=True,
            detailed=True,
            namespace=namespace
        )

        try:
            for details, items in iterator:
                if details is not None:
                    loading_bar.set_postfix(**details)

                for item in items:
                    writer.writerow(item)

                loading_bar.update(len(items))

        except CrowdTangleInvalidTokenError:
            loading_bar.close()
            die([
                'Your API token is invalid.',
                'Check that you indicated a valid one using the `--token` argument.'
            ])

        loading_bar.close()

    return action
