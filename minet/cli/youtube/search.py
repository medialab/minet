# =============================================================================
# Minet Youtube Search CLI Action
# =============================================================================
#
# Action searching videos using YouTube's API.
#
from itertools import islice

from minet.cli.utils import with_enricher_and_loading_bar
from minet.youtube import YouTubeAPIClient
from minet.youtube.types import YouTubeVideoSnippet


@with_enricher_and_loading_bar(
    headers=YouTubeVideoSnippet,
    title="Searching videos",
    unit="queries",
    sub_unit="videos",
    nested=True,
)
def action(cli_args, enricher, loading_bar):
    client = YouTubeAPIClient(cli_args.key)

    for row, query in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(query):
            searcher = client.search(query, order=cli_args.order)

            if cli_args.limit:
                searcher = islice(searcher, cli_args.limit)

            for video in searcher:
                loading_bar.nested_advance()
                enricher.writerow(row, video)
