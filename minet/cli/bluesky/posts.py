from typing import Iterable, Iterator
from casanova import Enricher

import casanova.ndjson as ndjson
import casanova

from ebbe import outer_zip

from twitwi.bluesky.constants import POST_FIELDS
from twitwi.bluesky.types import BlueskyPost
from twitwi.bluesky import format_post_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar, with_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=POST_FIELDS,
    title="Getting Bluesky posts from URIs or URLs",
    unit="posts",
    nested=False,
)
def action_normalize(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    def work(users: Iterable[str]) -> Iterator[BlueskyPost]:
        return client.get_posts(
            [
                param
                if param.startswith(
                    "at://did:"
                )  # In case the user passed full URLs instead of at:// URIs
                else client.post_url_to_did_at_uri(param)
                for param in users
            ]
        )

    for (row, _), post in outer_zip(
        enricher.cells(cli_args.column, with_rows=True), key=lambda x: x[1], work=work
    ):
        post_row = format_post_as_csv_row(post)
        enricher.writerow(row, post_row)
        loading_bar.advance()


@with_bluesky_fatal_errors
@with_loading_bar(
    title="Getting raw Bluesky posts from URIs or URLs",
    unit="posts",
    nested=False,
)
def action_raw(cli_args, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    reader = casanova.reader(cli_args.input, total=cli_args.total)
    writer = ndjson.writer(cli_args.output)

    params: list[str] = list(reader.cells(cli_args.column, with_rows=False))

    # with loading_bar.step(count=len(params)):
    for post in client.get_posts(
        [
            param
            if param.startswith(
                "at://did:"
            )  # In case the user passed full URLs instead of at:// URIs
            else client.post_url_to_did_at_uri(param)
            for param in params
        ],
        return_raw=True,
    ):
        writer.writerow(post)
        loading_bar.advance()


def action(cli_args):
    if cli_args.raw:
        action_raw(cli_args)
    else:
        action_normalize(cli_args)
