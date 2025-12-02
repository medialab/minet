from typing import Iterable, Iterator, Optional

from casanova import Enricher

import casanova.ndjson as ndjson
import casanova

from ebbe import outer_zip

from twitwi.bluesky.constants import PROFILE_FIELDS
from twitwi.bluesky import format_profile_as_csv_row
from twitwi.bluesky.types import BlueskyProfile

from minet.cli.utils import with_enricher_and_loading_bar, with_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient
from minet.bluesky.exceptions import BlueskyHandleNotFound


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=PROFILE_FIELDS,
    title="Getting Bluesky profiles from handles or DIDs",
    unit="profiles",
)
def action_normalize(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    def mixed_handles_and_dids_to_dids(profiles: Iterable[str]) -> Iterator[Optional[str]]:
        for profile in profiles:
            if profile.startswith("did:"):
                yield profile
            else:
                try:
                    yield client.resolve_handle(profile, True)
                except BlueskyHandleNotFound:
                    # in case the profile does not exist
                    yield None
                except Exception as e:
                    raise e

    def work(profiles: Iterable[str]) -> Iterator[BlueskyProfile]:
        dids = mixed_handles_and_dids_to_dids(profiles)
        return client.profiles(dids)

    for (row, _), profile in outer_zip(
        enricher.cells(cli_args.column, with_rows=True),
        key=lambda x: x[1],
        work=work,
    ):
        with loading_bar.step():
            profile_row = format_profile_as_csv_row(profile) if profile else None
            enricher.writerow(row, profile_row)


@with_bluesky_fatal_errors
@with_loading_bar(
    title="Getting Bluesky profiles from handles or DIDs",
    unit="profiles",
)
def action_raw(cli_args, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    reader = casanova.reader(cli_args.input, total=cli_args.total)
    writer = ndjson.writer(cli_args.output)

    params = reader.cells(cli_args.column, with_rows=False)

    def mixed_handles_and_dids_to_dids(profiles: Iterable[str]) -> Iterator[Optional[str]]:
        for profile in profiles:
            if profile.startswith("did:"):
                yield profile
            else:
                try:
                    yield client.resolve_handle(profile, True)
                except KeyError:  # in case the profile does not exist
                    yield None
                except Exception as e:
                    raise e

    def work(dids: Iterable[str]) -> Iterator[str]:
        return client.profiles(dids, return_raw=True)

    dids = mixed_handles_and_dids_to_dids(params)

    loading_bar.set_total(reader.total)

    for did, profile_payload in outer_zip(dids, key=lambda x: x, work=work):
        with loading_bar.step():
            writer.writerow({"did": did, "profile": profile_payload})


def action(cli_args):
    if cli_args.raw:
        action_raw(cli_args)
    else:
        action_normalize(cli_args)
