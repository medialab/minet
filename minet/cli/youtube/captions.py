# =============================================================================
# Minet Youtube Captions CLI Action
# =============================================================================
#
# Action retrieving the captions of YouTube videos using the API.
#
import casanova

from minet.cli.utils import LoadingBar
from minet.youtube import get_video_captions
from minet.youtube.constants import YOUTUBE_CAPTIONS_CSV_HEADERS


def captions_action(cli_args):
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=YOUTUBE_CAPTIONS_CSV_HEADERS,
        keep=cli_args.select,
    )

    loading_bar = LoadingBar("Retrieving captions", unit="video")

    for row, video in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.update()

        result = get_video_captions(video, langs=cli_args.lang)

        if result is None:
            continue

        track, lines = result

        prefix = [track.lang, "1" if track.generated else ""]

        for line in lines:
            enricher.writerow(row, prefix + list(line))
