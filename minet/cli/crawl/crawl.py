# =============================================================================
# Minet Crawl CLI Action
# =============================================================================
#
# Logic of the crawl action.
#
from typing import Optional, List, Callable, Any

import os
import casanova
import casanova.ndjson as ndjson
from inspect import isclass
from os.path import join, dirname
from ebbe.decorators import with_defer

from minet.utils import import_target
from minet.fs import FilenameBuilder
from minet.cli.exceptions import FatalError
from minet.crawl import (
    Crawler,
    CrawlResult,
    SuccessfulCrawlResult,
    SpiderDeclaration,
    Spider,
)
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
            self.__add_file(None, "data", crawler.get_spider())
        else:
            self.dir = join(base_dir, "data")
            for name, spider in crawler.spiders():
                self.__add_file(name, join("data", name), spider)

    def __add_file(self, name: Optional[str], path: str, spider):
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
            w = casanova.InferringWriter(f, add=["job_id"])
        elif self.format == "jsonl" or self.format == "ndjson":
            w = ndjson.writer(f)
        else:
            raise NotImplementedError('unknown format "%s"' % self.format)

        self.handles[name] = {"file": f, "writer": w, "spider": spider}

    def unpack_result(self, result: CrawlResult, data):
        job_id = result.job.id

        if self.format == "csv":
            return (data, [job_id])

        return ({"job_id": job_id, "data": data},)

    # NOTE: write is flushing to ensure atomicity as well as possible
    def write(self, result: CrawlResult) -> None:
        if self.singular:
            handle = self.handles[None]
            # TODO: factorize
            for item in handle["spider"].tabulate(result):
                handle["writer"].writerow(*self.unpack_result(result, item))
            handle["file"].flush()
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
def action(
    cli_args,
    defer=None,
    loading_bar: Optional[LoadingBar] = None,
    target: Optional[SpiderDeclaration] = None,
    additional_job_fieldnames: Optional[List[str]] = None,
    format_job_row_addendum: Optional[Callable[[CrawlResult], List]] = None,
    result_callback: Optional[Callable[[Any, LoadingBar, CrawlResult], None]] = None,
    write_data: bool = True,
):
    if (additional_job_fieldnames is not None and format_job_row_addendum is None) or (
        additional_job_fieldnames is None and format_job_row_addendum is not None
    ):
        raise TypeError("additional_job_fieldnames requires format_job_row_addendum")

    # NOTE: typing and decorators don't play well toegether
    assert defer is not None
    assert isinstance(loading_bar, LoadingBar)

    persistent_storage_path = join(cli_args.output_dir, "store")
    writer_root_directory = join(cli_args.output_dir, "pages")

    filename_builder = FilenameBuilder(cli_args.folder_strategy)

    def callback(self: Crawler, result: SuccessfulCrawlResult) -> None:
        if not cli_args.write_files:
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

    if cli_args.write_files:
        jobs_fieldnames += ["path"]

    if additional_job_fieldnames is not None:
        jobs_fieldnames += additional_job_fieldnames

    jobs_writer = casanova.Writer(jobs_output, fieldnames=jobs_fieldnames)
    defer(jobs_output.close)

    if target is None:
        try:
            target = import_target(cli_args.target, "spider")
        except ImportError:
            raise FatalError(
                [
                    "Could not import %s!" % cli_args.target,
                    "Are you sure the module exists?",
                ]
            )

        # Is target a Spider class?
        if isclass(target) and issubclass(target, Spider):
            target = target()
        elif not callable(target):
            # TODO: explain further
            raise FatalError("Invalid crawling target %s!" % cli_args.target)

    crawler = Crawler(
        target,
        throttle=cli_args.throttle,
        max_depth=cli_args.max_depth,
        persistent_storage_path=persistent_storage_path,
        writer_root_directory=writer_root_directory,
        visit_urls_only_once=cli_args.visit_urls_only_once,
        normalized_url_cache=cli_args.normalized_url_cache,
        resume=cli_args.resume,
        max_workers=cli_args.threads,
        callback=callback,
        wait=False,
        daemonic=False,
    )

    with crawler:
        if crawler.finished:
            loading_bar.erase()
            raise FatalError("[error]Crawler has already finished!")

        if crawler.resuming:
            loading_bar.print("[log.time]Crawler will now resume…")
        elif cli_args.input:
            for url in casanova.reader(cli_args.input).cells(cli_args.column):
                crawler.enqueue(url)  # type: ignore

        data_writer = None

        if write_data and cli_args.write_data:
            data_writer = DataWriter(
                cli_args.output_dir,
                crawler,
                resume=cli_args.resume,
                format=cli_args.format,
            )
            defer(data_writer.close)

        if not crawler.resuming and len(crawler) == 0:
            raise FatalError(
                [
                    "Started a crawler without any jobs.",
                    "This can happen if the command was given no start url nor -i/--input flag.",
                    "You can also implement start urls/targets on your spiders themselves if required.",
                    "Or maybe you forgot to --resume?",
                ],
                warning=True,
            )

        track_crawler_state_with_loading_bar(loading_bar, crawler.state)

        # Running crawler
        for result in crawler:
            with loading_bar.step():
                if result_callback is not None:
                    result_callback(cli_args, loading_bar, result)

                if cli_args.verbose:
                    console.print(result, highlight=True)

                job_row = result.as_csv_row()

                if cli_args.write_files:
                    job_row += [getattr(result, "_path", "")]

                if format_job_row_addendum is not None:
                    job_row += format_job_row_addendum(result)

                jobs_writer.writerow(job_row)

                # Flushing to avoid sync issues as well as possible
                jobs_output.flush()

                if result.error is not None:
                    loading_bar.inc_stat(result.error_code, style="error")
                    continue

                if data_writer is not None:
                    data_writer.write(result)
