from casanova import Enricher

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=["uri"],
    title="Getting Bluesky URIs",
    unit="url",
    nested=True,
)
def action(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    for row, url in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(f"{url}", sub_total=1):
            uri = client.resolve_post_url(url)
            enricher.writerow(row, [uri])
            loading_bar.nested_advance()
