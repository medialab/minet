# =============================================================================
# Minet Spotify Episodes By ID CLI Action
# =============================================================================
#
# Logic of the `sp episodes-by-id` action.
#

from ebbe import as_chunks

from minet.cli.utils import with_enricher_and_loading_bar
from minet.spotify import SpotifyAPIClient, SpotifyShowEpisode
from minet.spotify.utils import parse_chunk, parse_spotify_id


@with_enricher_and_loading_bar(
    headers=SpotifyShowEpisode.fieldnames(),
    title="Retrieving podcast episodes",
    unit="queries",
    sub_unit="episodes",
    nested=True,
)
def action(cli_args, enricher, loading_bar):
    client = SpotifyAPIClient(cli_args.client_id, cli_args.client_secret)

    for chunk in as_chunks(50, enricher.cells(cli_args.column, with_rows=True)):
        with loading_bar.step(count=len(chunk)):
            episode_ids = [parse_spotify_id(id) for _, id in parse_chunk(chunk)]

            indexed_result = {}
            for result in client.get_by_id(
                episode_ids,
                "episodes",
                cli_args.market,
                SpotifyShowEpisode.from_payload,
            ):
                indexed_result[result.id] = result

            for row, episode in parse_chunk(chunk):
                episode_id = parse_spotify_id(episode)
                addendum = indexed_result.get(episode_id)
                enricher.writerow(row, addendum)
