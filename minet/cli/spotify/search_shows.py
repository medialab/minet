# =============================================================================
# Minet Spotify Search-Shows CLI Action
# =============================================================================
#
# Logic of the `sp search-shows` action.
#

from minet.cli.utils import with_enricher_and_loading_bar
from minet.spotify import SpotifyAPIClient, SpotifyShow


@with_enricher_and_loading_bar(
    headers=SpotifyShow.fieldnames(),
    title="Retrieving podcast shows",
    unit="queries",
    sub_unit="shows",
    nested=True,
)
def action(cli_args, enricher, loading_bar):
    client = SpotifyAPIClient(cli_args.client_id, cli_args.client_secret)

    for row, query in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(query):
            for show in client.search(
                query, "show", cli_args.market, SpotifyShow.from_payload
            ):
                enricher.writerow(row, show)
                loading_bar.nested_advance()
