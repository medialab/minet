# =============================================================================
# Minet Crawl CLI Action
# =============================================================================
#
# Logic of the crawl action.
#
from typing import List, Any, Optional, Union, TextIO, Tuple

import os
import casanova
from os.path import join, isfile, isdir, dirname
from ebbe.decorators import with_defer

from minet.cli.exceptions import FatalError
from minet.cli.console import console
from minet.scrape import Scraper
from minet.scrape.exceptions import InvalidScraperError
from minet.crawl import Crawler, CrawlResult, CrawlerState, DefinitionSpiderOutput
from minet.cli.reporters import report_error, report_scraper_validation_errors
from minet.cli.loading_bar import LoadingBar
from minet.cli.utils import (
    with_loading_bar,
    with_ctrl_c_warning,
    track_crawler_state_with_loading_bar,
)

JOBS_HEADERS = [
    "spider",
    "depth",
    "url",
    "error",
    "status",
    "encoding",
    "degree",
    "scraped",
]

STATUS_TO_STYLE = {
    "acked": "success_background",
    "ready": "info_background",
    "unack": "warning_background",
    "ack_failed": "error_background",
}


def format_result_for_csv(
    result: CrawlResult[Any, DefinitionSpiderOutput], count: Optional[int] = None
) -> List[Optional[Union[str, int]]]:
    if result.error is not None:
        return [
            result.job.spider,
            result.job.depth,
            result.job.url,
            report_error(result.error),
            "",
            "",
            "",
            "",
            "",
        ]

    response = result.response

    assert response is not None

    return [
        result.job.spider,
        result.job.depth,
        result.job.url,
        "",
        response.status,
        response.encoding,
        result.degree,
        count,
    ]


def open_report(
    path: str, headers: List[str], resume: bool = False
) -> Tuple[TextIO, casanova.Writer]:
    flag = "w"

    if resume and isfile(path):
        flag = "a"

    os.makedirs(dirname(path), exist_ok=True)

    f = open(path, flag, encoding="utf-8")
    writer = casanova.writer(f)

    if flag == "w":
        writer.writerow(headers)

    return f, writer


class ScraperReporter(object):
    def __init__(self, path: str, scraper: Scraper, resume=False):
        if scraper.fieldnames is None:
            raise NotImplementedError("Scraper fieldnames could not be inferred.")

        f, writer = open_report(path, scraper.fieldnames, resume)

        self.fieldnames = scraper.fieldnames
        self.file = f
        self.writer = writer

    def write(self, items) -> int:
        count = 0

        # TODO: maybe abstract this once step above
        if not isinstance(items, list):
            items = [items]

        for item in items:
            count += 1

            if not isinstance(item, dict):
                self.writer.writerow([item])
                continue

            row = [item.get(k, "") for k in self.fieldnames]
            self.writer.writerow(row)

        return count

    def flush(self):
        self.file.flush()

    def close(self):
        self.file.close()


class ScraperReporterPool(object):
    SINGULAR = "$SINGULAR$"

    def __init__(self, crawler: Crawler, output_dir: str, resume=False):
        self.reporters = {}

        if crawler.singular:
            spider = crawler.get_spider()

            self.reporters["default"] = {}

            if spider.scraper is not None:
                path = join(output_dir, "scraped.csv")
                reporter = ScraperReporter(path, spider.scraper, resume)
                self.reporters["default"][ScraperReporterPool.SINGULAR] = reporter

            for name, scraper in spider.scrapers.items():
                path = join(output_dir, "scraped", "%s.csv" % name)

                reporter = ScraperReporter(path, scraper, resume)
                self.reporters["default"][name] = reporter
        else:
            for spider_name, spider in crawler.spiders.items():
                self.reporters[spider_name] = {}

                if spider.scraper is not None:
                    path = join(output_dir, "scraped", spider_name, "scraped.csv")
                    reporter = ScraperReporter(path, spider.scraper, resume)
                    self.reporters[spider_name][ScraperReporterPool.SINGULAR] = reporter

                for name, scraper in spider.scrapers.items():
                    path = join(output_dir, "scraped", spider_name, "%s.csv" % name)

                    reporter = ScraperReporter(path, scraper, resume)
                    self.reporters[spider_name][name] = reporter

    def write(self, spider_name: Optional[str], scraped: DefinitionSpiderOutput) -> int:
        count = 0

        if spider_name is None:
            spider_name = "default"

        reporter = self.reporters[spider_name]

        if scraped.default is not None:
            count += reporter[ScraperReporterPool.SINGULAR].write(scraped.default)

        for name, items in scraped.named.items():
            count += reporter[name].write(items)

        return count

    def __iter__(self):
        for spider_reporters in self.reporters.values():
            for reporter in spider_reporters.values():
                yield reporter

    def flush(self) -> None:
        for reporter in self:
            reporter.flush()

    def close(self) -> None:
        for reporter in self:
            reporter.close()


@with_defer()
@with_loading_bar(
    title="Crawling",
    unit="pages",
    stats=[
        {"name": "queued", "style": "info"},
        {"name": "doing", "style": "warning"},
        {"name": "done", "style": "success"},
    ],
)
@with_ctrl_c_warning
def action(cli_args, defer, loading_bar: LoadingBar):

    if cli_args.dump_queue and not isdir(cli_args.output_dir):
        loading_bar.erase()
        raise FatalError("Cannot dump crawl not started yet!")

    # Loading crawler definition
    queue_path = join(cli_args.output_dir, "queue")

    # Scaffolding output directory
    os.makedirs(cli_args.output_dir, exist_ok=True)

    jobs_output_path = join(cli_args.output_dir, "jobs.csv")
    jobs_output, jobs_writer = open_report(
        jobs_output_path, JOBS_HEADERS, resume=cli_args.resume
    )
    defer(jobs_output.close)

    # Creating crawler
    try:
        crawler = Crawler.from_definition(
            cli_args.crawler,
            throttle=cli_args.throttle,
            queue_path=queue_path,
            resume=cli_args.resume,
            wait=False,
            daemonic=False,
        )
    except InvalidScraperError as error:
        raise FatalError(
            [
                "Your scraper is invalid! You need to fix the following errors:\n",
                report_scraper_validation_errors(error.validation_errors),
            ]
        )

    if cli_args.dump_queue:
        loading_bar.erase()
        dump = crawler.dump_queue()
        for (status, job) in dump:
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
        crawler.stop()
        raise FatalError("[error]Crawler has already finished!")

    if crawler.resuming:
        loading_bar.print("[log.time]Will now resume…")

    with crawler:

        # Reporter pool
        reporter_pool = ScraperReporterPool(
            crawler, cli_args.output_dir, resume=cli_args.resume
        )
        defer(reporter_pool.close)

        track_crawler_state_with_loading_bar(loading_bar, crawler.state)

        # Running crawler
        for result in crawler:
            with loading_bar.step():
                if result.error is not None:
                    loading_bar.inc_stat(report_error(result.error), style="error")
                    jobs_writer.writerow(format_result_for_csv(result))
                    continue

                count = reporter_pool.write(result.job.spider, result.data)
                jobs_writer.writerow(format_result_for_csv(result, count=count))
                loading_bar.inc_stat("scraped", count=count, style="success")

                # Flushing to avoid sync issues as well as possible
                jobs_output.flush()
                reporter_pool.flush()
