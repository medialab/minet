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

    def mixed_urls_and_uris_to_uris(params: Iterable[str]) -> Iterator[str]:
        for param in params:
            # In case the user passed full URLs instead of at:// URIs
            if param.startswith("at://did:"):
                yield param
            else:
                yield client.resolve_post_url(param)

    def work(params: Iterable[str]) -> Iterator[BlueskyPost]:
        uris = mixed_urls_and_uris_to_uris(params)
        return client.posts(uris)

    for (row, _), post in outer_zip(
        enricher.cells(cli_args.column, with_rows=True), key=lambda x: x[1], work=work
    ):
        with loading_bar.step():
            post_row = format_post_as_csv_row(post) if post else None
            enricher.writerow(row, post_row)


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

    params = reader.cells(cli_args.column, with_rows=False)

    def mixed_urls_and_uris_to_uris(params: Iterable[str]) -> Iterator[str]:
        for param in params:
            # In case the user passed full URLs instead of at:// URIs
            if param.startswith("at://did:"):
                yield param
            else:
                yield client.resolve_post_url(param)

    def work(uris: Iterable[str]) -> Iterator[str]:
        return client.posts(uris, return_raw=True)

    uris = mixed_urls_and_uris_to_uris(params)

    loading_bar.set_total(reader.total)

    for uri, post_payload in outer_zip(uris, key=lambda x: x, work=work):
        with loading_bar.step():
            writer.writerow({"uri": uri, "post": post_payload})


def action(cli_args):
    if cli_args.raw:
        action_raw(cli_args)
    else:
        action_normalize(cli_args)
