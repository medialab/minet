from typing import Iterable, Iterator

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

    def work(users: Iterable[str]) -> Iterator[BlueskyProfile]:
        dids = []
        for user in users:
            if user.startswith("did:"):
                did = user
            else:
                try:
                    did = client.resolve_handle(user, True)
                except KeyError:  # in case the user does not exist
                    did = None
                except Exception as e:
                    raise e
            dids.append(did)
        return client.get_profiles(dids)

    with loading_bar.step(count=cli_args.total):
        for (row, _), profile in outer_zip(
            enricher.cells(cli_args.column, with_rows=True),
            key=lambda x: x[1],
            work=work,
        ):
            profile_row = format_profile_as_csv_row(profile) if profile else None
            enricher.writerow(row, profile_row)
            loading_bar.advance()
