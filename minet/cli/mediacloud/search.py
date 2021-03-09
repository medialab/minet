# =============================================================================
# Minet Mediacloud Search CLI Action
# =============================================================================
#
# Logic of the `mc search` action.
#
import csv

from minet.cli.utils import LoadingBar
from minet.mediacloud import MediacloudClient
from minet.mediacloud.constants import MEDIACLOUD_STORIES_CSV_HEADER
from minet.mediacloud.exceptions import MediacloudServerError


def mediacloud_search_action(namespace, output_file):
    writer = csv.writer(output_file)
    writer.writerow(MEDIACLOUD_STORIES_CSV_HEADER)

    client = MediacloudClient(namespace.token)

    kwargs = {
        'collections': namespace.collections,
        'medias': namespace.medias
    }

    loading_bar = LoadingBar(
        'Searching stories',
        unit='story',
        unit_plural='stories'
    )

    try:
        if not namespace.skip_count:
            count = client.count(
                namespace.query,
                **kwargs
            )

            loading_bar.update_total(count)

        iterator = client.search(
            namespace.query,
            format='csv_row',
            **kwargs
        )

        for story in iterator:
            writer.writerow(story)
            loading_bar.update()

    except MediacloudServerError as e:
        loading_bar.die([
            'Aborted due to a mediacloud server error:',
            e.server_error
        ])
