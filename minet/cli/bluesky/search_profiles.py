from casanova import Enricher

from twitwi.bluesky.constants import PARTIAL_PROFILE_FIELDS
from twitwi.bluesky import format_partial_profile_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=PARTIAL_PROFILE_FIELDS,
    title="Searching profiles",
    unit="queries",
    nested=True,
    sub_unit="profiles",
)
def action(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    if cli_args.limit:
        sub_total = int(cli_args.limit)
    else:
        sub_total = None

    for row, query in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(query, sub_total=sub_total, count=cli_args.total):
            for profile in client.search_profiles(query, limit=cli_args.limit):
                profile_row = format_partial_profile_as_csv_row(profile)
                enricher.writerow(row, profile_row)
                loading_bar.nested_advance()
