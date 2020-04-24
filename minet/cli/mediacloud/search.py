# =============================================================================
# Minet Mediacloud Search CLI Action
# =============================================================================
#
# Logic of the `mc search` action.
#
import csv
from tqdm import tqdm

from minet.mediacloud import MediacloudClient
from minet.mediacloud.constants import MEDIACLOUD_STORIES_CSV_HEADER


def mediacloud_search_action(namespace, output_file):
    writer = csv.writer(output_file)
    writer.writerow(MEDIACLOUD_STORIES_CSV_HEADER)

    client = MediacloudClient(namespace.token)

    count = client.count(namespace.query)

    loading_bar = tqdm(
        desc='Searching stories',
        dynamic_ncols=True,
        total=count,
        unit=' stories'
    )

    iterator = client.search(
        namespace.query,
        format='csv_row'
    )

    for story in iterator:
        writer.writerow(story)
        loading_bar.update()
