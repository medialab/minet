from ebbe.decorators import with_defer
import os
import casanova
from os.path import join, isdir

from minet.cli.crawl.crawl import open_report
from minet.cli.exceptions import FatalError
from minet.cli.console import console
from minet.crawl import Crawler, CrawlResult
from minet.crawl.focus import FocusSpider
from minet.cli.loading_bar import LoadingBar
from minet.cli.utils import (
    with_loading_bar,
    with_ctrl_c_warning,
    track_crawler_state_with_loading_bar,
)

ADDITIONAL_JOBS_HEADERS = ["relevant", "matches"]

STATUS_TO_STYLE = {
    "acked": "success_background",
    "ready": "info_background",
    "unack": "warning_background",
    "ack_failed": "error_background",
}


@with_defer()
@with_loading_bar(
    title="Focus crawling",
    unit="pages",
    stats=[
        {"name": "queued", "style": "info"},
        {"name": "doing", "style": "warning"},
        {"name": "done", "style": "success"},
        {"name": "irrelevant", "style": "warning"},
    ],
)
@with_ctrl_c_warning
def action(cli_args, defer, loading_bar: LoadingBar):
    if cli_args.dump_queue and not isdir(cli_args.output_dir):
        loading_bar.erase()
        raise FatalError("Cannot dump crawl not started yet!")

    # Getting all URLs
    keep_irrelevant = cli_args.keep_irrelevant
    reader = casanova.reader(cli_args.input)
    start_urls = reader.cells(cli_args.column)

    # Creating focus spider

    spider = FocusSpider(
        start_urls,
        max_depth=cli_args.max_depth,
        regex_content=cli_args.regex_content,
        regex_url=cli_args.regex_url,
        irrelevant_continue=cli_args.irrelevant_continue,
        only_target_html_page=cli_args.only_html,
        extract=cli_args.extract,
    )

    # Loading crawler definition
    persistent_storage_path = join(cli_args.output_dir, "store")

    # Scaffolding output directory
    os.makedirs(cli_args.output_dir, exist_ok=True)

    jobs_output_path = join(cli_args.output_dir, "jobs.csv")
    jobs_output, jobs_writer = open_report(
        jobs_output_path,
        CrawlResult.FIELDNAMES + ADDITIONAL_JOBS_HEADERS,
        resume=cli_args.resume,
    )
    defer(jobs_output.close)

    # Creating crawler
    crawler = Crawler(
        spider,
        throttle=cli_args.throttle,
        persistent_storage_path=persistent_storage_path,
        wait=False,
        daemonic=False,
        visit_urls_only_once=True,
        normalized_url_cache=True,
        resume=cli_args.resume or cli_args.dump_queue,
    )

    if cli_args.dump_queue:
        loading_bar.erase()
        dump = crawler.dump_queue()
        for status, job in dump:
            console.print(
                "[{style}]{status}[/{style}] depth=[warning]{depth}[/warning] {url}".format(
                    style=STATUS_TO_STYLE.get(status, "log.time"),
                    status=status,
                    depth=job.depth,
                    url=job.url,
                ),
                no_wrap=True,
                overflow="ellipsis",
            )

        console.print("Total:", "[success]{}".format(len(dump)))
        crawler.stop()
        return

    if crawler.finished:
        loading_bar.erase()
        raise FatalError("[error]Crawler has already finished!")

    if crawler.resuming:
        loading_bar.print("[log.time]Will now resume…")

    with crawler:
        # Reporter pool
        track_crawler_state_with_loading_bar(loading_bar, crawler.state)

        # Running crawler
        for result in crawler:
            with loading_bar.step():
                focus_rep = result.data

                inc_label = "crawled"
                inc_style = "success"
                inc_count = 1
                if result.error is not None:
                    inc_label = result.error_code
                    inc_style = "error"
                elif not focus_rep.relevant:
                    inc_label = "irrelevant"
                    inc_style = "warning"

                loading_bar.inc_stat(inc_label, count=inc_count, style=inc_style)

                if not focus_rep:
                    jobs_writer.writerow(result.as_csv_row() + [False, 0])
                    continue

                if not keep_irrelevant and (
                    result.error or not result.data or not focus_rep.relevant
                ):
                    continue

                jobs_writer.writerow(
                    result.as_csv_row(), [focus_rep.relevant, focus_rep.matches]
                )

                # Flushing to avoid sync issues as well as possible
                jobs_output.flush()
