# =============================================================================
# Minet Youtube Comments CLI Action
# =============================================================================
#
# Action retrieving the comments of YouTube videos using the API.
#
import sys
import casanova

from minet.cli.utils import LoadingBar, edit_cli_args_with_csv_io
from minet.youtube import YouTubeAPIClient
from minet.youtube.constants import YOUTUBE_COMMENT_CSV_HEADERS


def comments_action(cli_args, output_file):

    # Handling output
    single_video = cli_args.file is sys.stdin and sys.stdin.isatty()

    if single_video:
        edit_cli_args_with_csv_io(cli_args, 'video')

    enricher = casanova.enricher(
        cli_args.file,
        output_file,
        add=YOUTUBE_COMMENT_CSV_HEADERS,
        keep=cli_args.select
    )

    loading_bar = LoadingBar(
        'Retrieving comments',
        unit='comment',
        stats={'videos': 0}
    )

    def before_sleep_until_midnight(seconds):
        loading_bar.print('API limits reached. Will now wait until midnight Pacific time!')

    client = YouTubeAPIClient(
        cli_args.key,
        before_sleep_until_midnight=before_sleep_until_midnight
    )

    for row, video in enricher.cells(cli_args.column, with_rows=True):
        generator = client.comments(video)

        for comment in generator:
            loading_bar.update()
            enricher.writerow(row, comment.as_csv_row())

        loading_bar.inc('videos')

    loading_bar.close()
