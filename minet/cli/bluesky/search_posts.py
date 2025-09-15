from casanova import Enricher

from twitwi.bluesky.constants import POST_FIELDS
from twitwi.bluesky import format_post_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient

from itertools import islice


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

    wanted_flags = {
        "lang",
        "since",
        "until",
        "mentions",
        "author",
        "domain",
        "url",
        "limit",
    }

    limit = None

    flags_str: str = ""

    flags_list = []

    for flag, value in vars(cli_args).items():
        if flag in wanted_flags and value:
            if flag == "limit":
                limit = int(value)
            flags_list.append(f"{flag}:{value}")

    flags_str = "\n".join(flags_list)

    for row, query in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(
            f"{query}\n{flags_str}" if flags_str else query, sub_total=limit
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
                limit,
            ):
                post_row = format_post_as_csv_row(post)
                enricher.writerow(row, post_row)
                loading_bar.nested_advance()
