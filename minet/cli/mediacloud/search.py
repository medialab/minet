# =============================================================================
# Minet Mediacloud Search CLI Action
# =============================================================================
#
# Logic of the `mc search` action.
#
import csv

from minet.cli.utils import LoadingBar
from minet.mediacloud import MediacloudAPIClient
from minet.mediacloud.constants import MEDIACLOUD_STORIES_CSV_HEADER
from minet.mediacloud.exceptions import MediacloudServerError


def mediacloud_search_action(cli_args):
    writer = csv.writer(cli_args.output)
    writer.writerow(MEDIACLOUD_STORIES_CSV_HEADER)

    client = MediacloudAPIClient(cli_args.token)

    kwargs = {
        'collections': cli_args.collections,
        'medias': cli_args.medias,
        'publish_day': cli_args.publish_day,
        'publish_month': cli_args.publish_month,
        'publish_year': cli_args.publish_year,
        'filter_query': cli_args.filter_query
    }

    loading_bar = LoadingBar(
        'Searching stories',
        unit='story',
        unit_plural='stories'
    )

    try:
        if not cli_args.skip_count:
            count = client.count(
                cli_args.query,
                **kwargs
            )

            loading_bar.update_total(count)

        iterator = client.search(
            cli_args.query,
            **kwargs
        )

        for story in iterator:
            writer.writerow(story.as_csv_row())
            loading_bar.update()

    except MediacloudServerError as e:
        loading_bar.die([
            'Aborted due to a mediacloud server error:',
            e.server_error
        ])
