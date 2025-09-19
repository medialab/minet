from casanova import Enricher

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=["uri"],
    title="Resolving Bluesky handles",
    unit="handles",
    nested=True,
)
def action(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    for row, url in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(f"{url}", sub_total=1):
            uri = client.post_url_to_did_at_uri(url)
            enricher.writerow(row, [uri])
            loading_bar.nested_advance()
