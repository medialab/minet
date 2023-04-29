# =============================================================================
# Minet Spotify Shows CLI Action
# =============================================================================
#
# Logic of the `sp shows` action.
#

from minet.cli.utils import with_enricher_and_loading_bar
from minet.spotify import SpotifyAPIClient
from minet.spotify.constants import SPOTIFY_SHOW_HEADERS


@with_enricher_and_loading_bar(
    headers=SPOTIFY_SHOW_HEADERS,
    title="Retrieving podcast shows",
    unit="queries",
    sub_unit="shows",
    nested=True,
)
def action(cli_args, enricher, loading_bar):
    client = SpotifyAPIClient(
        cli_args.client_id,
        cli_args.client_secret,
        {"market": cli_args.market}
    )

    for row, query in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(query):
            for show in client.shows(query):
                enricher.writerow(row, show.as_csv_row())
                loading_bar.nested_advance()
