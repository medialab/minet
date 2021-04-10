# =============================================================================
# Minet Mediacloud Topic CLI Action
# =============================================================================
#
# Logic of the `mc topic` action.
#
import csv
from tqdm import tqdm

from minet.mediacloud import MediacloudAPIClient
from minet.mediacloud.constants import MEDIACLOUD_TOPIC_STORIES_CSV_HEADERS


def mediacloud_topic_action(cli_args, output_file):
    writer = csv.writer(output_file)
    writer.writerow(MEDIACLOUD_TOPIC_STORIES_CSV_HEADERS)

    loading_bar = tqdm(
        desc='Fetching stories',
        dynamic_ncols=True,
        unit=' stories'
    )

    client = MediacloudAPIClient(cli_args.token)

    iterator = client.topic_stories(
        cli_args.topic_id,
        media_id=cli_args.media_id,
        from_media_id=cli_args.from_media_id,
        format='csv_row'
    )

    for story in iterator:
        writer.writerow(story)
        loading_bar.update()
