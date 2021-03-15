# =============================================================================
# Minet Youtube Search CLI Action
# =============================================================================
#
# Action searching videos using YouTube's API.
#
import sys
import casanova
from itertools import islice

from minet.cli.utils import LoadingBar, edit_namespace_with_csv_io
from minet.youtube import YouTubeAPIClient
from minet.youtube.constants import YOUTUBE_VIDEO_SNIPPET_CSV_HEADERS


def search_action(namespace, output_file):

    # Handling output
    single_query = namespace.file is sys.stdin and sys.stdin.isatty()

    if single_query:
        edit_namespace_with_csv_io(namespace, 'query')

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        add=YOUTUBE_VIDEO_SNIPPET_CSV_HEADERS,
        keep=namespace.select
    )

    loading_bar = LoadingBar(
        'Searching videos',
        unit='video'
    )

    def before_sleep_until_midnight(seconds):
        loading_bar.print('API limits reached. Will now wait until midnight Pacific time!')

    client = YouTubeAPIClient(
        namespace.key,
        before_sleep_until_midnight=before_sleep_until_midnight
    )

    for row, query in enricher.cells(namespace.column, with_rows=True):
        loading_bar.print('Searching for "%s"' % query)

        searcher = client.search(query, order=namespace.order)

        if namespace.limit:
            searcher = islice(searcher, namespace.limit)

        for video in searcher:
            loading_bar.update()
            enricher.writerow(row, video.as_csv_row())

    loading_bar.close()
