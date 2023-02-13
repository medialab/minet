# =============================================================================
# Minet Mediacloud Medias CLI Action
# =============================================================================
#
# Logic of the `mc medias` action.
#
import csv
import casanova

from minet.cli.utils import LoadingBar
from minet.cli.mediacloud.utils import with_mediacloud_fatal_errors
from minet.mediacloud import MediacloudAPIClient
from minet.mediacloud.constants import (
    MEDIACLOUD_MEDIA_CSV_HEADER,
    MEDIACLOUD_FEED_CSV_HEADER,
)


@with_mediacloud_fatal_errors
def action(cli_args):
    added_headers = MEDIACLOUD_MEDIA_CSV_HEADER[1:]

    feeds_writer = None

    if cli_args.feeds:
        added_headers.append("feeds")
        feeds_writer = csv.writer(cli_args.feeds)
        feeds_writer.writerow(MEDIACLOUD_FEED_CSV_HEADER)

    enricher = casanova.enricher(
        cli_args.input, cli_args.output, keep=cli_args.select, add=added_headers
    )

    loading_bar = LoadingBar(desc="Fetching medias", unit="media", total=cli_args.total)

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

        loading_bar.update()
