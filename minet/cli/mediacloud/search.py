# =============================================================================
# Minet Mediacloud Search CLI Action
# =============================================================================
#
# Logic of the `mc search` action.
#
import casanova

from minet.cli.loading_bar import LoadingBar
from minet.cli.mediacloud.utils import with_mediacloud_fatal_errors
from minet.mediacloud import MediacloudAPIClient
from minet.mediacloud.constants import MEDIACLOUD_STORIES_CSV_HEADER


@with_mediacloud_fatal_errors
def action(cli_args):
    writer = casanova.writer(cli_args.output, fieldnames=MEDIACLOUD_STORIES_CSV_HEADER)

    client = MediacloudAPIClient(cli_args.token)

    kwargs = {
        "collections": cli_args.collections,
        "medias": cli_args.medias,
        "publish_day": cli_args.publish_day,
        "publish_month": cli_args.publish_month,
        "publish_year": cli_args.publish_year,
        "filter_query": cli_args.filter_query,
    }

    with LoadingBar(title="Searching", unit="stories") as loading_bar:
        if not cli_args.skip_count:
            count = client.count(cli_args.query, **kwargs)
            loading_bar.set_total(count)

        iterator = client.search(cli_args.query, **kwargs)

        for story in iterator:
            writer.writerow(story.as_csv_row())
            loading_bar.advance()
