# =============================================================================
# Minet Youtube Captions CLI Action
# =============================================================================
#
# Action retrieving the captions of YouTube videos using the API.
#
from minet.youtube import YouTubeScraper
from minet.youtube.types import YouTubeCaptionTrack, YouTubeCaptionLine
from minet.youtube.exceptions import YouTubeInvalidVideoTargetError

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar


def get_headers(cli_args):
    headers = YouTubeCaptionTrack.fieldnames(prefix="caption_track_")

    if cli_args.collapse:
        return headers + ["caption_track_text"]

    return headers + YouTubeCaptionLine.fieldnames(prefix="caption_line_")


@with_enricher_and_loading_bar(
    headers=get_headers, title="Retrieving captions", unit="videos"
)
def action(cli_args, enricher, loading_bar: LoadingBar):
    scraper = YouTubeScraper()

    lang_warning_printed = False

    for row, video in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step():
            try:
                result = scraper.get_video_captions(video, langs=cli_args.lang)
            except YouTubeInvalidVideoTargetError:
                loading_bar.inc_stat("not-a-video", style="error")
                continue

            if result is None:
                if not lang_warning_printed:
                    lang_warning_printed = True
                    loading_bar.warning(
                        "Did you forget to pass the correct value to [dim]--lang[/dim]?"
                    )

                loading_bar.inc_stat("not-found", style="error")
                continue

            track, lines = result

            if cli_args.collapse:
                enricher.writerow(row, track, ["\n".join(line.text for line in lines)])
            else:
                for line in lines:
                    enricher.writerow(row, track, line)
