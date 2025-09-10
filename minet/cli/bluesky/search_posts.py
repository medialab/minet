from casanova import Enricher

from twitwi.bluesky.constants import POST_FIELDS
from twitwi.bluesky import format_post_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient

import re


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

    flags_str = ""
    if cli_args.lang:
        flags_str += f"\nlang:{cli_args.lang}"
    if cli_args.since:
        flags_str += f"\nsince:{cli_args.since}"
    if cli_args.until:
        flags_str += f"\nuntil:{cli_args.until}"
    if cli_args.mentions:
        cli_args.mentions = re.sub(r"^@?", "", cli_args.mentions)
        flags_str += f"\nmentions:{cli_args.mentions}"
    if cli_args.author:
        cli_args.author = re.sub(r"^@?", "", cli_args.author)
        flags_str += f"\nauthor:{cli_args.author}"
    if cli_args.domain:
        flags_str += f"\ndomain:{cli_args.domain}"
    if cli_args.url:
        flags_str += f"\nurl:{cli_args.url}"
    if cli_args.tag:
        cli_args.tag = [re.sub(r"^#?", "", tag) for tag in cli_args.tag.split(" ")]
        flags_str += f"\ntag:{cli_args.tag}"
    if cli_args.not_keywords:
        cli_args.not_keywords = cli_args.not_keywords.split(" ")
        flags_str += f"\nnot:{cli_args.not_keywords}"

    for row, query in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(f"{query}{flags_str}"):
            for post in client.search_posts(
                query,
                lang=cli_args.lang,
                since=cli_args.since,
                until=cli_args.until,
                mentions=cli_args.mentions,
                author=cli_args.author,
                domain=cli_args.domain,
                url=cli_args.url,
                tag=cli_args.tag,
                not_keywords=cli_args.not_keywords,
            ):
                post_row = format_post_as_csv_row(post)
                enricher.writerow(row, post_row)
                loading_bar.nested_advance()
