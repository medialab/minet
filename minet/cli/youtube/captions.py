# =============================================================================
# Minet Youtube Captions CLI Action
# =============================================================================
#
# Action retrieving the captions of YouTube videos using the API.
#
import sys
import casanova

from minet.cli.utils import LoadingBar, edit_cli_args_with_csv_io
from minet.youtube import get_video_captions
from minet.youtube.constants import YOUTUBE_CAPTIONS_CSV_HEADERS


def captions_action(cli_args, output_file):

    # Handling output
    single_video = cli_args.file is sys.stdin and sys.stdin.isatty()

    if single_video:
        edit_cli_args_with_csv_io(cli_args, 'video')

    enricher = casanova.enricher(
        cli_args.file,
        output_file,
        add=YOUTUBE_CAPTIONS_CSV_HEADERS,
        keep=cli_args.select
    )

    loading_bar = LoadingBar(
        'Retrieving captions',
        unit='video'
    )

    for row, video in enricher.cells(cli_args.column, with_rows=True):
        result = get_video_captions(video, langs=cli_args.lang)
        loading_bar.update()

        if result is None:
            continue

        track, lines = result

        prefix = [track.lang, '1' if track.generated else '']

        for line in lines:
            enricher.writerow(row, prefix + list(line))

    loading_bar.close()
