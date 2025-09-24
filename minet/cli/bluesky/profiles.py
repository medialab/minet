from itertools import islice
from casanova import Enricher

from twitwi.bluesky.constants import PROFILE_FIELDS
from twitwi.bluesky import format_profile_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=PROFILE_FIELDS,
    title="Getting Bluesky profiles from handles or DIDs",
    unit="profiles",
    nested=True,
)
def action(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    # NOTE: Implement batching as itertools.batch is only available in Python 3.12+
    def batched(iterable, n, *, strict=False):
        if n < 1:
            raise ValueError("n must be at least one")
        iterator = iter(iterable)
        while batch := tuple(islice(iterator, n)):
            if strict and len(batch) != n:
                raise ValueError("batched(): incomplete batch")
            yield batch

    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    for batch in batched(enricher.cells(cli_args.column, with_rows=True), 25):
        users = [
            user if user.startswith("did:") else client.resolve_handle(user, True)
            for _, user in batch
        ]
        with loading_bar.step(sub_total=len(batch), count=len(batch)):
            for (row, _), profile in zip(batch, client.get_profiles(users)):
                profile_row = format_profile_as_csv_row(profile)
                enricher.writerow(row, profile_row)
                loading_bar.nested_advance()
