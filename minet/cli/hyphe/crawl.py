from typing import List, Any

import casanova
from collections import Counter

from minet.crawl import CrawlResult
from minet.hyphe import HypheSpider, HypheSpiderAddendum

from minet.cli.console import console
from minet.cli.crawl.crawl import crawl_action


def action(cli_args):
    spider = HypheSpider(ignore_internal_links=cli_args.ignore_internal_links)

    reader = casanova.reader(cli_args.corpus)
    headers = reader.headers

    assert headers is not None

    id_pos = headers[cli_args.id_column]
    status_pos = headers[cli_args.status_column]
    prefixes_pos = headers[cli_args.prefixes_column]
    start_pages_pos = headers.get(cli_args.start_pages_column)

    status_counts = Counter()
    webentity_count = 0

    for row in reader:
        webentity = row[id_pos]
        status = row[status_pos] or "IN"
        prefixes = row[prefixes_pos]

        if not prefixes:
            continue

        webentity_count += 1
        status_counts[status] += 1

        for prefix in prefixes.split(cli_args.prefix_separator):
            spider.set(prefix, webentity, status=status)

            if status == "IN":
                spider.add_start_page(prefix)

        if status != "IN" or start_pages_pos is None:
            continue

        start_pages = row[start_pages_pos]

        if not start_pages:
            continue

        for start_page in start_pages.split(cli_args.start_page_separator):
            spider.add_start_page(start_page)

    # Report
    console.print(
        "Indexed [success]%i[/success] webentities through [success]%i[/success] prefixes."
        % (webentity_count, len(spider.trie))
    )
    console.print("  [success]IN[/success]: %i" % status_counts["IN"])
    console.print("  [error]OUT[/error]: %i" % status_counts["OUT"])
    console.print("  [dim]UNDECIDED[/dim]: %i" % status_counts["UNDECIDED"])
    console.print("  [info]DISCOVERED[/info]: %i" % status_counts["DISCOVERED"])
    console.print(
        "Registered [success]%i[/success] start pages" % len(spider.start_pages)
    )

    def format_job_row_addendum(result: CrawlResult[Any, HypheSpiderAddendum]) -> List:
        info = result.data

        if not info:
            url = result.job.url
            webentity = spider.trie.match(url)

            assert webentity is not None

            return [webentity.id]

        return [info.webentity_id]

    return crawl_action(
        cli_args,
        target=spider,
        additional_job_fieldnames=["webentity"],
        format_job_row_addendum=format_job_row_addendum,
    )
