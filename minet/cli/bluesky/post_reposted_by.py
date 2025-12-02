from casanova import Enricher

from itertools import islice

from twitwi.bluesky.constants import PARTIAL_PROFILE_FIELDS
from twitwi.bluesky import format_partial_profile_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=PARTIAL_PROFILE_FIELDS,
    title="Getting list of reposts for Bluesky posts",
    unit="posts",
    nested=True,
    sub_unit="users",
)
def action(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    if cli_args.limit:
        sub_total = int(cli_args.limit)
    else:
        sub_total = None

    for row, param in enricher.cells(cli_args.column, with_rows=True):
        if param.startswith("at://did:"):
            uri = param
        else:
            uri = client.resolve_post_url(param)
        with loading_bar.step(uri, sub_total=sub_total):
            for profile in islice(client.post_reposted_by(uri), sub_total):
                repost_row = format_partial_profile_as_csv_row(profile)
                enricher.writerow(row, repost_row)
                loading_bar.nested_advance()
