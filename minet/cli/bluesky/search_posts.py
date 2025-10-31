from casanova import Enricher
from itertools import islice

import casanova.ndjson as ndjson

from twitwi.bluesky.constants import POST_FIELDS
from twitwi.bluesky import format_post_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar
from minet.cli.console import console

from minet.bluesky import BlueskyHTTPClient
from minet.cli.bluesky.utils import with_bluesky_fatal_errors


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=POST_FIELDS,
    title="Searching posts",
    unit="queries",
    nested=True,
    sub_unit="posts",
)
def action(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    cli_args.mentions = cli_args.mentions.lstrip("@") if cli_args.mentions else None
    cli_args.author = cli_args.author.lstrip("@") if cli_args.author else None
    if cli_args.store_errors:
        mode = "w" if cli_args.overwrite_errors else "a"
        errors_file = open(cli_args.store_errors, mode, encoding="utf-8")
        writer = ndjson.writer(errors_file)
    else:
        writer = None

    wanted_flags = [
        "lang",
        "since",
        "until",
        "mentions",
        "author",
        "domain",
        "url",
        "limit",
    ]

    flags_list = []

    for flag in wanted_flags:
        value = getattr(cli_args, flag, None)
        if value:
            flags_list.append(f"{flag}:{value}")

    flags_str: str = "\n".join(flags_list)

    nb_errors = 0
    for row, query in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(
            f"{query}\n{flags_str}" if flags_str else query,
            sub_total=int(cli_args.limit) if cli_args.limit else None,
        ):
            for post in islice(
                client.search_posts(
                    query,
                    lang=cli_args.lang,
                    since=cli_args.since,
                    until=cli_args.until,
                    mentions=cli_args.mentions,
                    author=cli_args.author,
                    domain=cli_args.domain,
                    url=cli_args.url,
                    store_errors=writer is not None,
                ),
                int(cli_args.limit) if cli_args.limit else None,
            ):
                if writer is not None and isinstance(post, tuple):
                    nb_errors += 1
                    console.print(
                        f"Total of errors encountered: {nb_errors}",
                        style="dim",
                        highlight=True,
                    )
                    error_message, post_payload = post
                    writer.writerow({"error": error_message, "post": post_payload})
                    errors_file.flush()
                    continue
                post_row = format_post_as_csv_row(post, allow_erroneous_plurals=True)
                enricher.writerow(row, post_row)
                loading_bar.nested_advance()
