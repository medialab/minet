from casanova import Enricher
from itertools import islice
import os
from datetime import datetime
import threading
from typing import Iterator

from twitwi.bluesky.constants import POST_FIELDS
from twitwi.bluesky.types import BlueskyPost
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
        lock_on_file = threading.Lock()

        def run(query, client: BlueskyHTTPClient, since, until) -> Iterator[BlueskyPost]:
            for post in client.search_posts(
                    query,
                    lang=cli_args.lang,
                    since=since,
                    until=until,
                    mentions=cli_args.mentions,
                    author=cli_args.author,
                    domain=cli_args.domain,
                    url=cli_args.url,
                ):
                yield post

        def batched(iterable, n, *, strict=False):
            # batched('ABCDEFG', 2) → AB CD EF G
            if n < 1:
                raise ValueError('n must be at least one')
            iterator = iter(iterable)
            while batch := tuple(islice(iterator, n)):
                if strict and len(batch) != n:
                    raise ValueError('batched(): incomplete batch')
                yield batch

        def work(row, query, client: BlueskyHTTPClient, since, until):
            for batch in islice(batched(run(query, client, since, until), 95), int(cli_args.limit) if cli_args.limit else None):
                lock_on_file.acquire()
                for post in batch:
                    post_row = format_post_as_csv_row(post)
                    enricher.writerow(row, post_row)
                    loading_bar.nested_advance()
                lock_on_file.release()

        clients = {}
        passwords = cli_args.passwords.split(",")
        for i in range(len(passwords)*2):
            # Using the same password twice to double the number of clients
            client = BlueskyHTTPClient(cli_args.identifier, passwords[i//2])
            clients[i] = (client, False)
            if len(clients) >= os.cpu_count()//1.5:
                break

        queries = []
        for row, query in enricher.cells(cli_args.column, with_rows=True):
            queries.append((row, query, cli_args.since, cli_args.until))

        # If not enough queries, we devide them to make sure all clients are used
        while len(queries) < (cli_args.subqueries or len(clients) * 2):
            new_queries = []
            # precedent_query = None
            # precedent_since = None
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

        from minet.cli.console import console

        threads : dict[int, tuple[BlueskyHTTPClient, threading.Thread]] = {}
        with loading_bar.step(
                f"{query}",
                sub_total=int(cli_args.limit) if cli_args.limit else None,
            ):
            def printing():
                console.print(f"Threads: {len(threads)} / Clients [bold green]working[/bold green]: {len([client_working for client_working in [working for _, working in clients.values()] if client_working])} / Clients [bold red]not working[/bold red]: {len([client_not_working for client_not_working in [working for _, working in clients.values()] if not client_not_working])} / Queries left: {len(queries)}", highlight=True)
            while queries:
                if len(threads) < len(clients):
                    for client_id, (client, working) in clients.copy().items():
                        if working:
                            continue
                        if not queries:
                            break
                        row, query, since, until = queries.pop()
                        clients[client_id] = (client, True)
                        thread = threading.Thread(
                            target=work,
                            args=(row, query, client, since, until),
                        )
                        threads[client_id] = (client, thread)
                        thread.start()
                        printing()
                for client_id, (_, thread) in threads.copy().items():
                    if not thread.is_alive():
                        clients[client_id] = (clients[client_id][0], False)
                        del threads[client_id]
                        printing()

            for _, thread in threads.values():
                thread.join()
                printing()


