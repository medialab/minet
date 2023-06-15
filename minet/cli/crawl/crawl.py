# =============================================================================
# Minet Crawl CLI Action
# =============================================================================
#
# Logic of the crawl action.
#
from typing import List, TextIO, Tuple

import os
import casanova
from os.path import join, isfile, dirname
from ebbe.decorators import with_defer

from minet.utils import import_target
from minet.cli.exceptions import FatalError
from minet.crawl import Crawler, CrawlResult, CrawlJob, Spider
from minet.cli.console import console
from minet.cli.loading_bar import LoadingBar
from minet.cli.utils import (
    with_loading_bar,
    with_ctrl_c_warning,
    track_crawler_state_with_loading_bar,
)

# NOTE: here are the possible file structure for scraped data:
#
# 1. singular spider, one group:
#    - data.csv
# 2. singular spider, multiple groups:
#    - data/
#      - group1.csv
#      - group2.csv
# 3. plural spider, one group:
#    - data/
#      - spider1.csv
#      - spider2.csv
# 4. plural spider, multiple groups
#    - data/
#      - spider1/
#        - group1.csv

# TODO: rely on casanova resumers?

# class ScraperReporter(object):
#     def __init__(self, path: str, scraper: Scraper, resume=False):
#         if scraper.fieldnames is None:
#             raise NotImplementedError("Scraper fieldnames could not be inferred.")

#         f, writer = open_report(path, ["job_id"] + scraper.fieldnames, resume)

#         self.fieldnames = scraper.fieldnames
#         self.file = f
#         self.writer = writer

#     def write(self, job_id: str, items) -> int:
#         count = 0

#         # TODO: maybe abstract this once step above
#         if not isinstance(items, list):
#             items = [items]

#         for item in items:
#             count += 1

#             if not isinstance(item, dict):
#                 row = [item]
#             else:
#                 row = [item.get(k, "") for k in self.fieldnames]

#             row = [job_id] + row

#             self.writer.writerow(row)

#         return count

#     def flush(self):
#         self.file.flush()

#     def close(self):
#         self.file.close()


# class ScraperReporterPool(object):
#     SINGULAR = object()

#     def __init__(self, crawler: Crawler, output_dir: str, resume=False):
#         self.reporters = {}

#         if crawler.singular:
#             spider = crawler.get_spider()

#             self.reporters["default"] = {}

#             if spider.scraper is not None:
#                 path = join(output_dir, "scraped.csv")
#                 reporter = ScraperReporter(path, spider.scraper, resume)
#                 self.reporters["default"][ScraperReporterPool.SINGULAR] = reporter

#             for name, scraper in spider.scrapers.items():
#                 path = join(output_dir, "scraped", "%s.csv" % name)

#                 reporter = ScraperReporter(path, scraper, resume)
#                 self.reporters["default"][name] = reporter
#         else:
#             for spider_name, spider in crawler.spiders.items():
#                 self.reporters[spider_name] = {}

#                 if spider.scraper is not None:
#                     path = join(output_dir, "scraped", spider_name, "scraped.csv")
#                     reporter = ScraperReporter(path, spider.scraper, resume)
#                     self.reporters[spider_name][ScraperReporterPool.SINGULAR] = reporter

#                 for name, scraper in spider.scrapers.items():
#                     path = join(output_dir, "scraped", spider_name, "%s.csv" % name)

#                     reporter = ScraperReporter(path, scraper, resume)
#                     self.reporters[spider_name][name] = reporter

#     def write(self, job: CrawlJob, scraped: DefinitionSpiderOutput) -> int:
#         count = 0

#         spider_name = job.spider

#         if spider_name is None:
#             spider_name = "default"

#         reporter = self.reporters[spider_name]

#         if scraped.default is not None:
#             count += reporter[ScraperReporterPool.SINGULAR].write(
#                 job.id, scraped.default
#             )

#         for name, items in scraped.named.items():
#             count += reporter[name].write(job.id, items)

#         return count

#     def __iter__(self):
#         for spider_reporters in self.reporters.values():
#             for reporter in spider_reporters.values():
#                 yield reporter

#     def flush(self) -> None:
#         for reporter in self:
#             reporter.flush()

#     def close(self) -> None:
#         for reporter in self:
#             reporter.close()


# NOTE: overhauling the way the crawler works.
# It should be able to import a spider instance, a crawler instance, a dict of spider instances, a callable, a spider class, a crawler class


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
    # Loading crawler definition
    persistent_storage_path = join(cli_args.output_dir, "store")

    # Scaffolding output directory
    os.makedirs(cli_args.output_dir, exist_ok=True)

    jobs_output_path = join(cli_args.output_dir, "jobs.csv")
    jobs_output = (
        casanova.BasicResumer(jobs_output_path, encoding="utf-8")
        if cli_args.resume
        else open(jobs_output_path, encoding="utf-8")
    )
    jobs_writer = casanova.Writer(jobs_output, fieldnames=CrawlResult.fieldnames())
    defer(jobs_output.close)

    target = import_target(cli_args.target, "spider")

    if not callable(target):
        # TODO: explain further
        raise FatalError("invalid crawling target")

    crawler = Crawler(
        target,
        throttle=cli_args.throttle,
        max_depth=cli_args.max_depth,
        persistent_storage_path=persistent_storage_path,
        visit_urls_only_once=cli_args.visit_urls_only_once,
        normalized_url_cache=cli_args.normalized_url_cache,
        resume=cli_args.resume,
        wait=False,
        daemonic=False,
    )

    if crawler.finished:
        loading_bar.erase()
        crawler.stop()
        raise FatalError("[error]Crawler has already finished!")

    if crawler.resuming:
        loading_bar.print("[log.time]Crawler will now resume…")
    else:
        # -s/--start-url
        if cli_args.start_url is not None:
            crawler.enqueue(cli_args.start_url)

        # TODO: -i, -s and variant for specific spiders

    with crawler:
        # Reporter pool
        # reporter_pool = ScraperReporterPool(
        #     crawler, cli_args.output_dir, resume=cli_args.resume
        # )
        # defer(reporter_pool.close)

        track_crawler_state_with_loading_bar(loading_bar, crawler.state)

        # Running crawler
        for result in crawler:
            # TODO: verbose
            with loading_bar.step():
                if cli_args.verbose:
                    console.print(result, highlight=True)

                jobs_writer.writerow(result)
                jobs_output.flush()

                if result.error is not None:
                    loading_bar.inc_stat(result.error_code, style="error")
                    continue

                # count = reporter_pool.write(result.job, result.data)
                # loading_bar.inc_stat("scraped", count=count, style="success")

                # # Flushing to avoid sync issues as well as possible
                # reporter_pool.flush()
