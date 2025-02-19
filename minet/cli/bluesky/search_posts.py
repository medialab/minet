from casanova import Enricher

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient
from minet.bluesky.types import BlueskyPost


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=BlueskyPost,
    title="Searching posts",
    unit="queries",
    nested=True,
    sub_unit="posts",
)
def action(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    for row, query in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(query):
            for post in client.search_posts(query):
                enricher.writerow(row, post)
                loading_bar.nested_advance()
