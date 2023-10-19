# =============================================================================
# Minet Youtube Captions CLI Action
# =============================================================================
#
# Action retrieving the captions of YouTube videos using the API.
#
from minet.youtube import YouTubeScraper
from minet.youtube.types import YouTubeCaptionTrack, YouTubeCaptionLine

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

HEADERS = YouTubeCaptionTrack.fieldnames(
    prefix="caption_track_"
) + YouTubeCaptionLine.fieldnames(prefix="caption_line_")


@with_enricher_and_loading_bar(
    headers=HEADERS, title="Retrieving captions", unit="videos"
)
def action(cli_args, enricher, loading_bar: LoadingBar):
    scraper = YouTubeScraper()

    with loading_bar.step():
        for row, video in enricher.cells(cli_args.column, with_rows=True):
            result = scraper.get_video_captions(video, langs=cli_args.lang)

            if result is None:
                loading_bar.inc_stat("not-found", style="error")
                continue

            track, lines = result

            for line in lines:
                enricher.writerow(row, track, line)
