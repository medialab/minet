# =============================================================================
# Minet Crawl CLI Action
# =============================================================================
#
# Logic of the crawl action.
#
from typing import Optional, List, Callable, Any, Mapping, Union, cast

import os
import casanova
import casanova.ndjson as ndjson
from inspect import isclass
from os.path import join, dirname
from ebbe.decorators import with_defer

from minet.utils import import_target
from minet.fs import FilenameBuilder
from minet.exceptions import (
    GenericModuleNotFoundError,
    TargetInGenericModuleNotFoundError,
)
from minet.cli.exceptions import FatalError
from minet.crawl import (
    Crawler,
    CrawlResult,
    SuccessfulCrawlResult,
    SpiderDeclaration,
    Spider,
    BasicSpider,
)
from minet.crawl.exceptions import CrawlerAlreadyFinishedError
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
        self.dir = base_dir

        if self.singular:
            self.__add_file(None, "data", crawler.get_spider())
        else:
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

    def __unpack_result(self, result: SuccessfulCrawlResult, data):
        job_id = result.job.id

        if self.format == "csv":
            return (data, [job_id])

        return ({"job_id": job_id, "data": data},)

    def write(self, result: SuccessfulCrawlResult) -> None:
        handle = self.handles[result.spider]
        spider = handle["spider"]
        writer = handle["writer"]
        f = handle["file"]

        for item in spider.tabulate(result):
            writer.writerow(*self.__unpack_result(result, item))

        # NOTE: write is flushing to ensure atomicity as well as possible
        f.flush()

    def flush(self) -> None:
        for h in self.handles.values():
            h["file"].flush()

    def close(self) -> None:
        for h in self.handles.values():
            h["file"].close()


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
def crawl_action(
    cli_args,
    defer=None,
    loading_bar: Optional[LoadingBar] = None,
    target: Optional[Union[SpiderDeclaration, Callable[..., Crawler]]] = None,
    additional_job_fieldnames: Optional[List[str]] = None,
    format_job_row_addendum: Optional[Callable[[CrawlResult], List]] = None,
    result_callback: Optional[Callable[[Any, LoadingBar, CrawlResult], None]] = None,
):
    if (additional_job_fieldnames is not None and format_job_row_addendum is None) or (
        additional_job_fieldnames is None and format_job_row_addendum is not None
    ):
        raise TypeError("additional_job_fieldnames requires format_job_row_addendum")

    # NOTE: typing and decorators don't play well together
    assert defer is not None
    assert isinstance(loading_bar, LoadingBar)

    persistent_storage_path = join(cli_args.output_dir, "store")
    writer_root_directory = join(cli_args.output_dir, "pages")

    filename_builder = FilenameBuilder(cli_args.folder_strategy)

    def callback(self: Crawler, result: SuccessfulCrawlResult) -> Optional[str]:
        if not cli_args.write_files:
            return

        response = result.response
        filename = result.job.id

        path = filename_builder(
            url=response.end_url,
            filename=filename,
            compressed=cli_args.compress_on_disk,
            ext=response.ext,
        )

        self.write(path, response.body, compress=cli_args.compress_on_disk)

        return path

    # Scaffolding output directory
    os.makedirs(cli_args.output_dir, exist_ok=True)

    crawler_kwargs = {
        "persistent_storage_path": persistent_storage_path,
        "writer_root_directory": writer_root_directory,
        "resume": cli_args.resume,
        "wait": False,
        "daemonic": False,
    }

    # NOTE: the cli_args given to this action might lack some items
    # so that crawler factory are more convenient to use.
    cli_args_to_forward_to_crawler = [
        "throttle",
        "max_depth",
        "visit_urls_only_once",
        "normalized_url_cache",
        ("threads", "max_workers"),
        ("spoof_user_agent", "spoof_ua"),
        "insecure",
        "domain_parallelism",
        ("processes", "process_pool_workers"),
        "timeout",
        "stateful_redirects",
        ("pycurl", "use_pycurl"),
        ("compress_transfer", "compressed"),
        "sqlar",
    ]

    for arg in cli_args_to_forward_to_crawler:
        if isinstance(arg, tuple):
            cli_arg_name, crawler_arg_name = arg
        else:
            cli_arg_name = arg
            crawler_arg_name = arg

        if hasattr(cli_args, cli_arg_name):
            crawler_kwargs[crawler_arg_name] = getattr(cli_args, cli_arg_name)

    retries = getattr(cli_args, "retries", 0)

    if retries:
        crawler_kwargs["retry"] = True
        crawler_kwargs["retryer_kwargs"] = {
            "retry_on_timeout": True,
            "max_attempts": 1 + retries,
        }

    if target is None:
        if cli_args.module is not None:
            try:
                target = import_target(cli_args.module, "spider")
            except GenericModuleNotFoundError:
                raise FatalError(
                    [
                        "Could not import %s!" % cli_args.module,
                        "Are you sure the module exists?",
                    ]
                )
            except TargetInGenericModuleNotFoundError as e:
                raise FatalError(
                    [
                        "Could not find the %s target in the %s module!"
                        % (e.name, e.path),
                        "Are you sure this class/function/variable exists in the module?",
                    ]
                )
        else:
            target = BasicSpider()

    # NOTE: target can be:
    #   - a crawler factory function
    #   - a spider class
    #   - a spider instance
    #   - a dict of spider instances
    #   - a simple callable
    try:
        if not cli_args.factory:
            # Is target a Spider class?
            if isclass(target) and issubclass(target, Spider):
                target = target()
            else:
                # NOTE: at that point, target can be:
                #   - a Spider instance
                #   - a dict of Spider instances
                #   - a callable
                valid_spiders_dict = isinstance(target, Mapping) and all(
                    isinstance(v, Spider) for v in target.values()
                )

                # TODO: inspect arity to weed out potential footguns
                if (
                    not valid_spiders_dict
                    and not isinstance(target, Spider)
                    and not callable(target)
                ):
                    # TODO: explain further
                    raise FatalError("Invalid crawling target!")

            # NOTE: target IS a spider declaration
            target = cast(SpiderDeclaration, target)

            crawler = Crawler(target, **crawler_kwargs)

        else:
            if not callable(target):
                raise FatalError("Factory should be callable!")

            # NOTE: target is a crawler factory
            target = cast(Callable[..., Crawler], target)

            crawler = target(**crawler_kwargs)

            if not isinstance(crawler, Crawler):
                raise FatalError("Factory did not return a crawler!")

    except CrawlerAlreadyFinishedError:
        loading_bar.erase()
        raise FatalError("[error]Crawler has already finished!")

    # Jobs output
    jobs_output_path = join(cli_args.output_dir, "jobs.csv")
    jobs_output = (
        casanova.BasicResumer(jobs_output_path, encoding="utf-8")
        if cli_args.resume
        else open(jobs_output_path, "w", encoding="utf-8")
    )
    jobs_fieldnames = CrawlResult.fieldnames(singular=crawler.singular)

    if cli_args.write_files:
        jobs_fieldnames += ["path"]

    if additional_job_fieldnames is not None:
        jobs_fieldnames += additional_job_fieldnames

    jobs_writer = casanova.Writer(jobs_output, fieldnames=jobs_fieldnames)
    defer(jobs_output.close)

    with crawler:
        # Enqueuing extraneous start jobs?
        if crawler.resuming:
            loading_bar.print("[log.time]Crawler will now resume…")
        elif getattr(cli_args, "input", None):
            for url in casanova.reader(cli_args.input).cells(cli_args.column):
                crawler.enqueue(url)  # type: ignore

        data_writer = None

        if cli_args.write_data:
            data_writer = DataWriter(
                cli_args.output_dir,
                crawler,
                resume=cli_args.resume,
                format=getattr(cli_args, "format", "csv"),
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
        for result, result_path in crawler.crawl(callback=callback):
            with loading_bar.step():
                if cli_args.verbose:
                    console.print(result, highlight=True)

                if result_callback is not None:
                    result_callback(cli_args, loading_bar, result)

                job_row = result.as_csv_row()

                if cli_args.write_files:
                    job_row += [result_path]

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


action = crawl_action
