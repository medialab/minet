# =============================================================================
# Minet Mediacloud Medias CLI Action
# =============================================================================
#
# Logic of the `mc medias` action.
#
import csv
import casanova
from tqdm import tqdm

from minet.cli.utils import die
from minet.mediacloud import MediacloudAPIClient
from minet.mediacloud.constants import (
    MEDIACLOUD_MEDIA_CSV_HEADER,
    MEDIACLOUD_FEED_CSV_HEADER
)
from minet.mediacloud.exceptions import MediacloudServerError


def mediacloud_medias_action(namespace, output_file):
    added_headers = MEDIACLOUD_MEDIA_CSV_HEADER[1:]

    feeds_file = None
    feeds_writer = None

    if namespace.feeds:
        added_headers.append('feeds')
        feeds_file = open(namespace.feeds, 'w', encoding='utf-8')
        feeds_writer = csv.writer(feeds_file)
        feeds_writer.writerow(MEDIACLOUD_FEED_CSV_HEADER)

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        keep=namespace.select,
        add=added_headers
    )

    loading_bar = tqdm(
        desc='Fetching medias',
        dynamic_ncols=True,
        unit=' medias',
        total=namespace.total
    )

    client = MediacloudAPIClient(namespace.token)

    for row, media_id in enricher.cells(namespace.column, with_rows=True):

        try:
            result = client.media(media_id, format='csv_row')

            if namespace.feeds:
                feeds = client.feeds(media_id, format='csv_row')

                enricher.writerow(row, result[1:] + [len(feeds)])

                for feed in feeds:
                    feeds_writer.writerow(feed)
            else:
                enricher.writerow(row, result[1:])
        except MediacloudServerError as e:
            loading_bar.close()
            die([
                'Aborted due to a mediacloud server error:',
                e.server_error
            ])

        loading_bar.update()

    feeds_file.close()
