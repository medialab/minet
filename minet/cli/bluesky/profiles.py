from typing import Iterable, Iterator, Optional

from casanova import Enricher

from ebbe import outer_zip

from twitwi.bluesky.constants import PROFILE_FIELDS
from twitwi.bluesky import format_profile_as_csv_row
from twitwi.bluesky.types import BlueskyProfile

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=PROFILE_FIELDS,
    title="Getting Bluesky profiles from handles or DIDs",
    unit="profiles",
)
def action(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    def mixed_handles_and_dids_to_dids(users: Iterable[str]) -> Iterator[Optional[str]]:
        for user in users:
            if user.startswith("did:"):
                yield user
            else:
                try:
                    yield client.resolve_handle(user, True)
                except KeyError:  # in case the user does not exist
                    yield None
                except Exception as e:
                    raise e

    def work(users: Iterable[str]) -> Iterator[BlueskyProfile]:
        dids = mixed_handles_and_dids_to_dids(users)
        return client.get_profiles(dids)

    for (row, _), profile in outer_zip(
        enricher.cells(cli_args.column, with_rows=True),
        key=lambda x: x[1],
        work=work,
    ):
        with loading_bar.step():
            profile_row = format_profile_as_csv_row(profile) if profile else None
            enricher.writerow(row, profile_row)
