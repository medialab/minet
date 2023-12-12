# =============================================================================
# Minet Mediacloud Medias CLI Action
# =============================================================================
#
# Logic of the `mc medias` action.
#
import casanova

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.mediacloud.utils import with_mediacloud_fatal_errors
from minet.mediacloud import MediacloudAPIClient
from minet.mediacloud.types import MediacloudFeed, MediacloudMedia


def get_headers(cli_args):
    headers = MediacloudMedia.fieldnames()[1:]

    if cli_args.feeds is not None:
        headers.append("feeds")

    return headers


@with_mediacloud_fatal_errors
@with_enricher_and_loading_bar(
    headers=get_headers, title="Fetching medias", unit="medias"
)
def action(cli_args, enricher, loading_bar):
    feeds_writer = None

    if cli_args.feeds:
        feeds_writer = casanova.writer(cli_args.feeds, fieldnames=MediacloudFeed)

    client = MediacloudAPIClient(cli_args.token)

    for row, media_id in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step():
            result = client.media(media_id)
            result = result.as_csv_row()[1:]

            if cli_args.feeds:
                assert feeds_writer is not None

                feeds = client.feeds(media_id)

                enricher.writerow(row, result + [len(feeds)])

                for feed in feeds:
                    feeds_writer.writerow(feed.as_csv_row())
            else:
                enricher.writerow(row, result)
