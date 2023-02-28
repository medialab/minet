# =============================================================================
# Minet Crawl CLI Action
# =============================================================================
#
# Logic of the crawl action.
#
from typing import List, Any, Optional, Union, TextIO, Tuple

import os
import casanova
from os.path import join, isfile, dirname
from shutil import rmtree
from ebbe.decorators import with_defer

from minet.cli.exceptions import FatalError
from minet.scrape import Scraper
from minet.scrape.exceptions import InvalidScraperError
from minet.crawl import Crawler, CrawlResult, DefinitionSpiderOutput
from minet.cli.reporters import report_error, report_scraper_validation_errors
from minet.cli.utils import with_loading_bar, with_ctrl_c_warning

JOBS_HEADERS = [
    "spider",
    "url",
    "resolved",
    "status",
    "error",
    "filename",
    "encoding",
    "next",
    "depth",
]


def format_job_for_csv(
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

    def close(self) -> None:
        for spider_reporters in self.reporters.values():
            for reporter in spider_reporters.values():
                reporter.close()


@with_defer()
@with_loading_bar(title="Crawling", unit="pages")
@with_ctrl_c_warning
def action(cli_args, defer, loading_bar):

    # Loading crawler definition
    queue_path = join(cli_args.output_dir, "queue")

    if cli_args.resume:
        loading_bar.print("[info]Will now resume…")
    else:
        rmtree(queue_path, ignore_errors=True)

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

    with crawler:

        # Reporter pool
        reporter_pool = ScraperReporterPool(
            crawler, cli_args.output_dir, resume=cli_args.resume
        )
        defer(reporter_pool.close)

        # TODO: update loading bar total using crawler state

        # Running crawler
        for result in crawler:
            with loading_bar.step():
                jobs_writer.writerow(format_job_for_csv(result))

                if result.error is not None:
                    loading_bar.inc_stat("errors", style="error")
                    continue

                reporter_pool.write(result.job.spider, result.output)
