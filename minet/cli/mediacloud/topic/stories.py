# =============================================================================
# Minet Mediacloud Topic CLI Action
# =============================================================================
#
# Logic of the `mc topic` action.
#
import casanova

from minet.cli.loading_bar import LoadingBar
from minet.mediacloud import MediacloudAPIClient
from minet.mediacloud.constants import MEDIACLOUD_TOPIC_STORIES_CSV_HEADERS


def action(cli_args):
    writer = casanova.writer(
        cli_args.output, fieldnames=MEDIACLOUD_TOPIC_STORIES_CSV_HEADERS
    )

    with LoadingBar(title="Fetching stories", unit="stories") as loading_bar:
        client = MediacloudAPIClient(cli_args.token)

        iterator = client.topic_stories(
            cli_args.topic_id,
            media_id=cli_args.media_id,
            from_media_id=cli_args.from_media_id,
        )

        for story in iterator:
            writer.writerow(story.as_csv_row())
            loading_bar.advance()
