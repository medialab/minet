# =============================================================================
# Minet Mediacloud Medias CLI Action
# =============================================================================
#
# Logic of the `mc medias` action.
#
import casanova
from tqdm import tqdm

from minet.cli.utils import die
from minet.mediacloud import MediacloudClient
from minet.mediacloud.constants import MEDIACLOUD_MEDIA_CSV_HEADER
from minet.mediacloud.exceptions import MediacloudServerError


def mediacloud_medias_action(namespace, output_file):
    enricher = casanova.enricher(
        namespace.file,
        output_file,
        keep=namespace.select,
        add=MEDIACLOUD_MEDIA_CSV_HEADER[1:]
    )

    loading_bar = tqdm(
        desc='Fetching medias',
        dynamic_ncols=True,
        unit=' medias',
        total=namespace.total
    )

    client = MediacloudClient(namespace.token)

    for row, media_id in enricher.cells(namespace.column, with_rows=True):

        try:
            result = client.media(media_id, format='csv_row')
            enricher.writerow(row, result[1:])
        except MediacloudServerError as e:
            loading_bar.close()
            die([
                'Aborted due to a mediacloud server error:',
                e.server_error
            ])

        loading_bar.update()
