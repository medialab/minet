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
from minet.mediacloud.constants import (
    MEDIACLOUD_MEDIA_CSV_HEADER,
    MEDIACLOUD_FEED_CSV_HEADER,
)


@with_mediacloud_fatal_errors
@with_enricher_and_loading_bar(
    headers=MEDIACLOUD_MEDIA_CSV_HEADER[1:], title="Fetching medias", unit="medias"
)
def action(cli_args, enricher, loading_bar):
    added_headers = MEDIACLOUD_MEDIA_CSV_HEADER[1:]

    feeds_writer = None

    if cli_args.feeds:
        added_headers.append("feeds")
        feeds_writer = casanova.writer(
            cli_args.feeds, fieldnames=MEDIACLOUD_FEED_CSV_HEADER
        )

    client = MediacloudAPIClient(cli_args.token)

    for row, media_id in enricher.cells(cli_args.column, with_rows=True):
        result = client.media(media_id)
        result = result.as_csv_row()[1:]

        if cli_args.feeds:
            feeds = client.feeds(media_id)

            enricher.writerow(row, result + [len(feeds)])

            for feed in feeds:
                feeds_writer.writerow(feed.as_csv_row())
        else:
            enricher.writerow(row, result)

        loading_bar.advance()
