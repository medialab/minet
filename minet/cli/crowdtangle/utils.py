# =============================================================================
# Minet CrowdTangle CLI Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the CrowdTangle actions.
#
import casanova
import casanova.ndjson as ndjson

from minet.cli.utils import print_err, with_fatal_errors
from minet.cli.loading_bar import LoadingBar
from minet.cli.exceptions import InvalidArgumentsError
from minet.crowdtangle import CrowdTangleAPIClient
from minet.crowdtangle.exceptions import CrowdTangleInvalidTokenError

FATAL_ERRORS = {
    CrowdTangleInvalidTokenError: [
        "Your API token is invalid.",
        "Check that you indicated a valid one using the `-t/--token` argument.",
    ]
}


def with_crowdtangle_fatal_errors(fn):
    return with_fatal_errors(FATAL_ERRORS)(fn)


def with_crowdtangle_client(fn):
    def wrapped(cli_args, *args, **kwargs):
        return fn(
            cli_args,
            *args,
            **{
                "client": CrowdTangleAPIClient(
                    cli_args.token, rate_limit=cli_args.rate_limit
                ),
                **kwargs,
            }
        )

    return wrapped


def with_crowdtangle_utilities(fn):
    return with_crowdtangle_fatal_errors(with_crowdtangle_client(fn))


def make_paginated_action(
    method_name, item_name, csv_headers, get_args=None, announce=None
):
    @with_crowdtangle_fatal_errors
    def action(cli_args):
        resume = getattr(cli_args, "resume", False)

        # Validation
        if resume:
            if cli_args.sort_by != "date":
                raise InvalidArgumentsError(
                    "Cannot --resume if --sort_by is not `date`."
                )

            if cli_args.format != "csv":
                raise InvalidArgumentsError("Cannot --resume jsonl format yet.")

        if cli_args.format == "csv":
            fieldnames = csv_headers(cli_args) if callable(csv_headers) else csv_headers
            writer = casanova.writer(cli_args.output, fieldnames=fieldnames)
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
            title="Fetching %s" % item_name, unit=item_name, total=cli_args.limit
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

        with loading_bar:
            for _, items in iterator:
                loading_bar.advance(len(items))

                # if details is not None:
                #     loading_bar.update_stats(**details)

                for item in items:
                    if cli_args.format == "csv":
                        item = item.as_csv_row()

                    writer.writerow(item)

    return action
