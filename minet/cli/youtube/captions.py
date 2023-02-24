# =============================================================================
# Minet Youtube Captions CLI Action
# =============================================================================
#
# Action retrieving the captions of YouTube videos using the API.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.youtube import get_video_captions
from minet.youtube.constants import YOUTUBE_CAPTIONS_CSV_HEADERS


@with_enricher_and_loading_bar(
    headers=YOUTUBE_CAPTIONS_CSV_HEADERS, title="Retrieving captions", unit="videos"
)
def action(cli_args, enricher, loading_bar):
    with loading_bar.step():
        for row, video in enricher.cells(cli_args.column, with_rows=True):
            result = get_video_captions(video, langs=cli_args.lang)

            if result is None:
                continue

            track, lines = result

            prefix = [track.lang, "1" if track.generated else ""]

            for line in lines:
                enricher.writerow(row, prefix + list(line))
