from casanova import Enricher

from itertools import islice

from twitwi.bluesky.constants import POST_FIELDS
from twitwi.bluesky import format_post_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=POST_FIELDS,
    title="Getting quotes from Bluesky posts",
    unit="posts",
    nested=True,
    sub_unit="quotes",
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
            for post in islice(client.quotes(uri), sub_total):
                quote_row = format_post_as_csv_row(post)
                enricher.writerow(row, quote_row)
                loading_bar.nested_advance()
