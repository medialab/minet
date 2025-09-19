from minet.bluesky import BlueskyHTTPClient
from minet.cli.argparse import PartialISODatetimeType

from casanova import Enricher
from itertools import islice

from twitwi.bluesky.constants import POST_FIELDS
from twitwi.bluesky import format_post_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

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

    # We accept partial ISO dates, but the API needs full datetimes
    if cli_args.since:
        cli_args.since = str(PartialISODatetimeType(True)(cli_args.since))
    if cli_args.until:
        cli_args.until = str(PartialISODatetimeType(True)(cli_args.until))

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
                ),
                int(cli_args.limit) if cli_args.limit else None,
            ):
                post_row = format_post_as_csv_row(post)
                enricher.writerow(row, post_row)
                loading_bar.nested_advance()
