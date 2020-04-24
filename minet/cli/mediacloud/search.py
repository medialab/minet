# =============================================================================
# Minet Mediacloud Search CLI Action
# =============================================================================
#
# Logic of the `mc search` action.
#
import csv
from tqdm import tqdm

from minet.mediacloud import MediacloudClient
# from minet.mediacloud.constants import MEDIACLOUD_TOPIC_STORIES_CSV_HEADERS


def mediacloud_search_action(namespace, output_file):
    # writer = csv.writer(output_file)
    # writer.writerow(MEDIACLOUD_TOPIC_STORIES_CSV_HEADERS)

    client = MediacloudClient(namespace.token)

    count = client.count(namespace.query)

    loading_bar = tqdm(
        desc='Searching stories',
        dynamic_ncols=True,
        total=count,
        unit=' stories'
    )

    # iterator = client.topic_stories(
    #     namespace.topic_id,
    #     media_id=namespace.media_id,
    #     from_media_id=namespace.from_media_id,
    #     format='csv_row'
    # )

    # for story in iterator:
    #     writer.writerow(story)
    #     loading_bar.update()
