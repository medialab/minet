# =============================================================================
# Minet CrowdTangle CLI Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the CrowdTangle actions.
#
import csv
import casanova
import ndjson

from minet.utils import prettyprint_seconds
from minet.cli.utils import print_err, die, LoadingBar
from minet.crowdtangle import CrowdTangleAPIClient
from minet.crowdtangle.exceptions import (
    CrowdTangleInvalidTokenError,
    CrowdTangleRateLimitExceeded,
    CrowdTangleInvalidJSONError
)


def make_paginated_action(method_name, item_name, csv_headers, get_args=None,
                          announce=None):

    def action(cli_args):

        # Do we need to resume?
        need_to_resume = False

        if getattr(cli_args, 'resume', False):
            need_to_resume = True

            if not cli_args.output_is_file:
                die(
                    'Cannot --resume without knowing where the output will be written (use -o/--output).',
                )

            if cli_args.sort_by != 'date':
                die('Cannot --resume if --sort_by is not `date`.')

            if cli_args.format != 'csv':
                die('Cannot --resume jsonl format yet.')

            last_cell = casanova.reverse_reader.last_cell(cli_args.output.name, 'datetime')

            if last_cell is not None:
                last_date = last_cell.replace(' ', 'T')
                cli_args.end_date = last_date

                print_err('Resuming from: %s' % last_date)

        if callable(announce):
            print_err(announce(cli_args))

        # Loading bar
        loading_bar = LoadingBar(
            desc='Fetching %s' % item_name,
            unit=item_name,
            total=cli_args.limit
        )

        if cli_args.format == 'csv':
            writer = csv.writer(cli_args.output)

            if not need_to_resume:
                writer.writerow(csv_headers(cli_args) if callable(csv_headers) else csv_headers)
        else:
            writer = ndjson.writer(cli_args.output)

        client = CrowdTangleAPIClient(cli_args.token, rate_limit=cli_args.rate_limit)

        args = []

        if callable(get_args):
            args = get_args(cli_args)

        def before_sleep(retry_state):
            exc = retry_state.outcome.exception()

            if isinstance(exc, CrowdTangleRateLimitExceeded):
                reason = 'Call failed because of rate limit!'

            elif isinstance(exc, CrowdTangleInvalidJSONError):
                reason = 'Call failed because of invalid JSON payload!'

            else:
                reason = 'Call failed because of server timeout!'

            loading_bar.print(
                '%s\nWill wait for %s before attempting again.' % (
                    reason,
                    prettyprint_seconds(retry_state.idle_for, granularity=2)
                )
            )

        create_iterator = getattr(client, method_name)
        iterator = create_iterator(
            *args,
            limit=cli_args.limit,
            format='csv_row' if cli_args.format == 'csv' else 'raw',
            per_call=True,
            detailed=True,
            namespace=cli_args,
            before_sleep=before_sleep
        )

        try:
            for details, items in iterator:
                loading_bar.update(len(items))

                if details is not None:
                    loading_bar.update_stats(**details)

                for item in items:
                    writer.writerow(item)

        except CrowdTangleInvalidTokenError:
            loading_bar.die([
                'Your API token is invalid.',
                'Check that you indicated a valid one using the `--token` argument.'
            ])

    return action
