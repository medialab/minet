# =============================================================================
# Minet Crawl CLI Action
# =============================================================================
#
# Logic of the crawl action.
#
from typing import List, TextIO, Tuple, Optional

import os
import casanova
import casanova.ndjson as ndjson
from os.path import join, isfile, dirname, relpath
from ebbe.decorators import with_defer

from minet.utils import import_target
from minet.fs import FilenameBuilder
from minet.cli.exceptions import FatalError
from minet.crawl import Crawler, CrawlResult, SuccessfulCrawlResult, CrawlJob, Spider
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
class DataWriter:
    def __init__(
        self, base_dir: str, crawler: Crawler, resume: bool = False, format: str = "csv"
    ):
        self.handles = {}
        self.resume = resume
        self.singular = crawler.singular
        self.format = format

        if self.singular:
            self.dir = base_dir
            self.__add_file(None, "data")
        else:
            self.dir = join(base_dir, "data")
            for name, _ in crawler.spiders():
                self.__add_file(name, join("data", name))

    def __add_file(self, name: Optional[str], path: str):
        path += "." + self.format

        path = join(self.dir, path)
        directory = dirname(path)
        os.makedirs(directory, exist_ok=True)

        f = (
            casanova.BasicResumer(path, encoding="utf-8")
            if self.resume
            else open(path, "w", encoding="utf-8")
        )

        if self.format == "csv":
            # TODO: ability to pass fieldnames? from spider?
            w = casanova.InferringWriter(f)
        elif self.format == "jsonl" or self.format == "ndjson":
            w = ndjson.writer(f)
        else:
            raise NotImplementedError('unknown format "%s"' % self.format)

        self.handles[name] = {"file": f, "writer": w}

    def write(self, result: CrawlResult) -> None:
        if self.singular:
            self.handles[None]["writer"].writerow(result.data)
        else:
            raise NotImplementedError

    def flush(self) -> None:
        for h in self.handles.values():
            h["file"].flush()

    def close(self) -> None:
        for h in self.handles.values():
            h["file"].close()


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
    persistent_storage_path = join(cli_args.output_dir, "store")
    writer_root_directory = join(cli_args.output_dir, "pages")

    filename_builder = FilenameBuilder(cli_args.folder_strategy)

    def callback(self: Crawler, result: SuccessfulCrawlResult) -> None:
        if not cli_args.write:
            return

        response = result.response
        filename = result.job.id

        path = filename_builder(
            url=response.end_url,
            filename=filename,
            compressed=cli_args.compress,
            ext=response.ext,
        )

        self.write(path, response.body, compress=cli_args.compress)

        setattr(result, "_path", path)

    # Scaffolding output directory
    os.makedirs(cli_args.output_dir, exist_ok=True)

    jobs_output_path = join(cli_args.output_dir, "jobs.csv")
    jobs_output = (
        casanova.BasicResumer(jobs_output_path, encoding="utf-8")
        if cli_args.resume
        else open(jobs_output_path, "w", encoding="utf-8")
    )
    jobs_fieldnames = CrawlResult.fieldnames()

    if cli_args.write:
        jobs_fieldnames += ["path"]

    jobs_writer = casanova.Writer(jobs_output, fieldnames=jobs_fieldnames)
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
        writer_root_directory=writer_root_directory,
        visit_urls_only_once=cli_args.visit_urls_only_once,
        normalized_url_cache=cli_args.normalized_url_cache,
        resume=cli_args.resume,
        callback=callback,
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

    data_writer = DataWriter(
        cli_args.output_dir, crawler, resume=cli_args.resume, format=cli_args.format
    )
    defer(data_writer.close)

    with crawler:
        track_crawler_state_with_loading_bar(loading_bar, crawler.state)

        # Running crawler
        for result in crawler:
            with loading_bar.step():
                if cli_args.verbose:
                    console.print(result, highlight=True)

                if cli_args.write:
                    jobs_writer.writerow(result, [getattr(result, "_path", "")])
                else:
                    jobs_writer.writerow(result)

                # Flushing to avoid sync issues as well as possible
                jobs_output.flush()

                if result.error is not None:
                    loading_bar.inc_stat(result.error_code, style="error")
                    continue

                data_writer.write(result)

                # Flushing to avoid sync issues as well as possible
                data_writer.flush()
