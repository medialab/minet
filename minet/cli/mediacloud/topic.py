# =============================================================================
# Minet Mediacloud Topic CLI Action
# =============================================================================
#
# Logic of the `mc topic` action.
#
import csv

from minet.cli.utils import LoadingBar
from minet.mediacloud import MediacloudAPIClient
from minet.mediacloud.constants import MEDIACLOUD_TOPIC_STORIES_CSV_HEADERS


def mediacloud_topic_action(cli_args):
    writer = csv.writer(cli_args.output)
    writer.writerow(MEDIACLOUD_TOPIC_STORIES_CSV_HEADERS)

    loading_bar = LoadingBar(
        desc="Fetching stories", unit="story", unit_plural="stories"
    )

    client = MediacloudAPIClient(cli_args.token)

    iterator = client.topic_stories(
        cli_args.topic_id,
        media_id=cli_args.media_id,
        from_media_id=cli_args.from_media_id,
    )

    for story in iterator:
        writer.writerow(story.as_csv_row())
        loading_bar.update()
