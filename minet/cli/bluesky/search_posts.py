from casanova import Enricher
from itertools import islice
from datetime import datetime
import threading

from typing import Iterator, List, Tuple
from quenouille import imap_unordered, NamedLocks

from twitwi.bluesky.constants import POST_FIELDS
from twitwi.bluesky import format_post_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

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

    cli_args.mentions = cli_args.mentions.lstrip("@") if cli_args.mentions else None
    cli_args.author = cli_args.author.lstrip("@") if cli_args.author else None

    if not cli_args.passwords:

        client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

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
    else:

        passwords = cli_args.passwords.split(",")
        number_of_times_to_use_a_password = 2


        def get_queries() -> Iterator[Tuple[List[str], str, str, str]]:
            queries = []
            for row, query in enricher.cells(cli_args.column, with_rows=True):
                queries.append((row, query, cli_args.since, cli_args.until))

            # Not dividing queries if limit is set, as we want to limit the total number of posts
            # for each query, not per sub-query
            if not cli_args.limit:
                # If not enough queries, we divide them to make sure all threads are used
                while len(queries) < len(passwords)*number_of_times_to_use_a_password:
                    new_queries = []
                    # Splitting each query in two, by date range
                    for (row, query, since, until) in queries:
                        if not since:
                            # Date of public release of Bluesky
                            since = "2024-02-06T00:00:00.000000Z"
                            new_queries.append((row, query, "0001-01-01T00:00:00.000000Z", since))
                        elif since <= "2024-02-06T00:00:00.000000Z":
                            # We don't split the query before Bluesky release date
                            # as posts quantity before this date is less dense
                            new_queries.append((row, query, since, until))
                            continue
                        if not until:
                            until = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S.%fZ")

                        since_dt = datetime.strptime(since, "%Y-%m-%dT%H:%M:%S.%fZ")
                        until_dt = datetime.strptime(until, "%Y-%m-%dT%H:%M:%S.%fZ")
                        middle_dt = since_dt + (until_dt - since_dt) / 2

                        middle_date = datetime.strftime(middle_dt, "%Y-%m-%dT%H:%M:%S.%fZ")
                        new_queries.append((row, query, since, middle_date))
                        new_queries.append((row, query, middle_date, until))

                    queries = new_queries

            for row, query, since, until in queries:
                yield (row, query, since, until)

        locks = NamedLocks()
        thread_data = threading.local()
        global password_index
        password_index = 0

        def initialize_client():
            with locks["passwords"]:
                global password_index
                password = passwords[password_index//number_of_times_to_use_a_password]
                password_index += 1


            thread_data.password_index = password_index
            thread_data.password = password

            with locks["cli_args"]:
                thread_data.client = BlueskyHTTPClient(cli_args.identifier, password)

        def batched(iterable, n, *, strict=False):
            # batched('ABCDEFG', 2) → AB CD EF G
            if n < 1:
                raise ValueError('n must be at least one')
            iterator = iter(iterable)
            while batch := tuple(islice(iterator, n)):
                if strict and len(batch) != n:
                    raise ValueError('batched(): incomplete batch')
                yield batch

        def work(item: Tuple[List[str], str, str, str]) -> Iterator[Tuple[List[str], List[str]]]:
            row, query, since, until = item

            # console.print(f"[bold green]Client {thread_data.password_index}[/bold green] ([purple]{thread_data.password}[/purple]) working on query: [yellow]{query}[/yellow]")

            for batch in batched(islice(thread_data.client.search_posts(
                    query,
                    lang=cli_args.lang,
                    since=since,
                    until=until,
                    mentions=cli_args.mentions,
                    author=cli_args.author,
                    domain=cli_args.domain,
                    url=cli_args.url,
                ), int(cli_args.limit) if cli_args.limit else None), 100):
                for post in batch:
                    post_row = format_post_as_csv_row(post)
                    with locks["enricher"]:
                        enricher.writerow(row, post_row)
                        loading_bar.nested_advance()



        for _ in imap_unordered(
            get_queries(),
            work,
            threads=len(passwords)*number_of_times_to_use_a_password,
            initializer=initialize_client,
            wait=False,
            daemonic=True,
        ):
            with locks["enricher"]:
                loading_bar.advance()