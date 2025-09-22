from casanova import Enricher

from twitwi.bluesky.constants import POST_FIELDS
from twitwi.bluesky import format_post_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=POST_FIELDS,
    title="Getting posts",
    unit="users",
    nested=True,
    sub_unit="posts",
)
def action(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    for row, user in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(user):
            for post in client.get_user_posts(user, limit=cli_args.limit):
                post_row = format_post_as_csv_row(post)
                enricher.writerow(row, post_row)
                loading_bar.nested_advance()
