from casanova import Enricher

from twitwi.bluesky.constants import PARTIAL_PROFILE_FIELDS
from twitwi.bluesky import format_partial_profile_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=PARTIAL_PROFILE_FIELDS,
    title="Getting Bluesky follows",
    unit="profiles",
    nested=True,
    sub_unit="follows",
)
def action(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    for row, user in enricher.cells(cli_args.column, with_rows=True):
        if not user.startswith("did:"):
            did = client.resolve_handle(user)
        else:
            did = user

        if cli_args.limit:
            sub_total = int(cli_args.limit)
        else:
            sub_total = next(client.get_profiles([did]))["follows"]

        with loading_bar.step(did, sub_total=sub_total):
            for follow in client.get_follows(did, cli_args.limit):
                follow_row = format_partial_profile_as_csv_row(follow)
                enricher.writerow(row, follow_row)
                loading_bar.nested_advance()
