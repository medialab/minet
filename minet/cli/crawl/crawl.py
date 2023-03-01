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
from minet.cli.utils import with_loading_bar, with_ctrl_c_warning

JOBS_HEADERS = [
    "spider",
    "url",
    "resolved",
    "status",
    "error",
    "filename",
    "encoding",
    "degree",
    "depth",
]

STATUS_TO_STYLE = {
    "acked": "success_background",
    "ready": "info_background",
    "unack": "warning_background",
    "ack_failed": "error_background",
}


def format_result_for_csv(
    result: CrawlResult[Any, DefinitionSpiderOutput]
) -> List[Optional[Union[str, int]]]:
    if result.error is not None:
        return [
            result.job.spider,
            result.job.url,
            "",
            "",
            report_error(result.error),
            "",
            "",
            "0",
            result.job.depth,
        ]

    response = result.response

    assert response is not None

    return [
        result.job.spider,
        result.job.url,
        response.end_url if response.was_redirected else "",
        response.status,
        "",
        "",
        response.encoding,
        result.degree,
        result.job.depth,
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
        if scraper.headers is None:
            raise NotImplementedError("Scraper headers could not be inferred.")

        f, writer = open_report(path, scraper.headers, resume)

        self.headers = scraper.headers
        self.file = f
        self.writer = writer

    def write(self, items):

        # TODO: maybe abstract this once step above
        if not isinstance(items, list):
            items = [items]

        for item in items:
            if not isinstance(item, dict):
                self.writer.writerow([item])
                continue

            row = [item.get(k, "") for k in self.headers]
            self.writer.writerow(row)

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

    def write(self, spider_name: Optional[str], scraped: DefinitionSpiderOutput):
        if spider_name is None:
            spider_name = "default"

        reporter = self.reporters[spider_name]

        if scraped.default is not None:
            reporter[ScraperReporterPool.SINGULAR].write(scraped.default)

        for name, items in scraped.named.items():
            reporter[name].write(items)

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

        def on_state_update(state: CrawlerState):
            loading_bar.set_total(state.total)
            loading_bar.set_stat("queued", state.jobs_queued)
            loading_bar.set_stat("doing", state.jobs_doing)
            loading_bar.set_stat("done", state.jobs_done)

        crawler.state.set_listener(on_state_update)

        # Running crawler
        for result in crawler:
            with loading_bar.step():
                jobs_writer.writerow(format_result_for_csv(result))

                if result.error is not None:
                    loading_bar.inc_stat("errors", style="error")
                    continue

                reporter_pool.write(result.job.spider, result.output)

                # Flushing to avoid sync issues as well as possible
                jobs_output.flush()
                reporter_pool.flush()
