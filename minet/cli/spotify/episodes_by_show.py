# =============================================================================
# Minet Spotify Episodes By Show CLI Action
# =============================================================================
#
# Logic of the `sp episodes-by-show` action.
#

from minet.cli.utils import with_enricher_and_loading_bar
from minet.spotify import SpotifyAPIClient, SpotifyShowEpisode


@with_enricher_and_loading_bar(
    headers=SpotifyShowEpisode.fieldnames(),
    title="Retrieving podcast episodes",
    unit="queries",
    sub_unit="episodes",
    nested=True,
)
def action(cli_args, enricher, loading_bar):
    client = SpotifyAPIClient(cli_args.client_id, cli_args.client_secret)

    for row, query in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(query):
            for episode in client.get_episodes_by_show_id(
                query, cli_args.market, SpotifyShowEpisode.from_payload
            ):
                enricher.writerow(row, episode)
                loading_bar.nested_advance()
