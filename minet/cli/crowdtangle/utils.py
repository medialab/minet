# =============================================================================
# Minet CrowdTangle CLI Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the CrowdTangle actions.
#
import casanova
import ndjson

from minet.cli.utils import print_err, die, LoadingBar
from minet.crowdtangle import CrowdTangleAPIClient
from minet.crowdtangle.exceptions import CrowdTangleInvalidTokenError


def make_paginated_action(
    method_name, item_name, csv_headers, get_args=None, announce=None
):
    def action(cli_args):

        resume = getattr(cli_args, "resume", False)

        # Validation
        if resume:
            if cli_args.sort_by != "date":
                die("Cannot --resume if --sort_by is not `date`.")

            if cli_args.format != "csv":
                die("Cannot --resume jsonl format yet.")

        if cli_args.format == "csv":
            fieldnames = csv_headers(cli_args) if callable(csv_headers) else csv_headers
            writer = casanova.writer(cli_args.output, fieldnames)
        else:
            writer = ndjson.writer(cli_args.output)

        # Acquiring state from resumer
        if getattr(cli_args, "resume", False):
            last_date = cli_args.output.pop_state()

            if last_date is not None:
                cli_args.end_date = last_date.replace(" ", "T")
                print_err("Resuming from: %s" % cli_args.end_date)

        if callable(announce):
            print_err(announce(cli_args))

        # Loading bar
        loading_bar = LoadingBar(
            desc="Fetching %s" % item_name, unit=item_name[:-1], total=cli_args.limit
        )

        args = []

        if callable(get_args):
            args = get_args(cli_args)

        client = CrowdTangleAPIClient(cli_args.token, rate_limit=cli_args.rate_limit)

        create_iterator = getattr(client, method_name)
        iterator = create_iterator(
            *args,
            limit=cli_args.limit,
            raw=cli_args.format != "csv",
            per_call=True,
            detailed=True,
            namespace=cli_args
        )

        try:
            for details, items in iterator:
                loading_bar.update(len(items))

                if details is not None:
                    loading_bar.update_stats(**details)

                for item in items:
                    if cli_args.format == "csv":
                        item = item.as_csv_row()

                    writer.writerow(item)

        except CrowdTangleInvalidTokenError:
            loading_bar.die(
                [
                    "Your API token is invalid.",
                    "Check that you indicated a valid one using the `--token` argument.",
                ]
            )

    return action
