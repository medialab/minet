from casanova import Enricher

from twitwi.bluesky.constants import MINIMAL_PROFILE_FIELDS
from twitwi.bluesky import format_minimal_profile_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=MINIMAL_PROFILE_FIELDS,
    title="Getting Bluesky followers",
    unit="profiles",
    nested=True,
    sub_unit="followers",
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
            sub_total = next(client.get_profiles([did]))["followers"]

        with loading_bar.step(did, sub_total=sub_total):
            for follower in client.get_followers(did, cli_args.limit):
                follower_row = format_minimal_profile_as_csv_row(follower)
                enricher.writerow(row, follower_row)
                loading_bar.nested_advance()
