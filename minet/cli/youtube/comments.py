# =============================================================================
# Minet Youtube Comments CLI Action
# =============================================================================
#
# Action retrieving the comments of YouTube videos using the API.
#
import sys
import casanova

from minet.cli.utils import LoadingBar, edit_namespace_with_csv_io
from minet.youtube import YouTubeAPIClient
from minet.youtube.constants import YOUTUBE_COMMENT_CSV_HEADERS


def comments_action(namespace, output_file):

    # Handling output
    single_video = namespace.file is sys.stdin and sys.stdin.isatty()

    if single_video:
        edit_namespace_with_csv_io(namespace, 'video')

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        add=YOUTUBE_COMMENT_CSV_HEADERS,
        keep=namespace.select
    )

    loading_bar = LoadingBar(
        'Retrieving comments',
        unit='comment',
        stats={'videos': 0}
    )

    def before_sleep_until_midnight(seconds):
        loading_bar.print('API limits reached. Will now wait until midnight Pacific time!')

    client = YouTubeAPIClient(
        namespace.key,
        before_sleep_until_midnight=before_sleep_until_midnight
    )

    for row, video in enricher.cells(namespace.column, with_rows=True):
        generator = client.comments(video)

        for comment in generator:
            loading_bar.update()
            enricher.writerow(row, comment.as_csv_row())

        loading_bar.inc('videos')

    loading_bar.close()
