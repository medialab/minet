from casanova import Enricher

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=["did"],
    title="Resolving Bluesky handles",
    unit="handles",
    nested=True,
)
def action(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    for row, handle in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(f"{handle}", sub_total=1):
            did = client.resolve_handle(handle)
            enricher.writerow(row, [did])
            loading_bar.nested_advance()
