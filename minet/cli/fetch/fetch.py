# =============================================================================
# Minet Fetch CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and fetching the urls found
# in the given column. This is done in a respectful multithreaded fashion to
# optimize both running time & memory.
#
from typing import Optional, List, Union

import casanova
from casanova import TabularRecord
from dataclasses import dataclass
from datetime import datetime
from ural import is_shortened_url, could_be_html

from minet.fetch import (
    FetchResult,
    FetchWorkerPayload,
    FetchThreadPoolExecutor,
    ResolveThreadPoolExecutor,
)
from minet.fs import FilenameBuilder, ThreadSafeFilesWriter
from minet.web import grab_cookies, parse_http_header, Response, RedirectionStack
from minet.exceptions import InvalidURLError, FilenameFormattingError
from minet.cli.exceptions import InvalidArgumentsError, FatalError
from minet.cli.reporters import report_error, report_filename_formatting_error
from minet.cli.utils import with_enricher_and_loading_bar, with_ctrl_c_warning


@dataclass
class FetchAddendum(TabularRecord):
    resolved_url: Optional[str] = None
    http_status: Optional[int] = None
    datetime_utc: Optional[datetime] = None
    fetch_error: Optional[str] = None
    filename: Optional[str] = None
    mimetype: Optional[str] = None
    encoding: Optional[str] = None

    def infos_from_response(self, response: Response) -> None:
        self.resolved_url = response.end_url if response.was_redirected else None
        self.http_status = response.status
        self.datetime_utc = response.end_datetime
        self.filename = response.get("filename")
        self.encoding = response.encoding
        self.mimetype = response.mimetype


@dataclass
class FetchAddendumWithBody(FetchAddendum):
    body: Optional[str] = None

    def infos_from_response(self, response: Response) -> None:
        super().infos_from_response(response)
        self.body = response.get("decoded_contents")


@dataclass
class ResolveAddendum(TabularRecord):
    resolved_url: Optional[str] = None
    http_status: Optional[int] = None
    resolution_error: Optional[str] = None
    redirect_count: Optional[int] = None
    redirect_chain: Optional[List[str]] = None

    def infos_from_stack(self, stack: RedirectionStack):
        last = stack[-1]

        self.resolved_url = last.url
        self.status = last.status
        self.redirect_count = len(stack) - 1
        self.redirect_chain = [step.type for step in stack]


def get_style_for_status(status: int) -> str:
    if status < 400:
        return "info"

    return "warning"


def loading_bar_stats_sort_key(item):
    name = item["name"]

    if isinstance(name, int):
        return (0, str(name))

    if name == "filtered":
        return (2, name)

    return (1, name)


def get_headers(cli_args):
    if cli_args.action == "resolve":
        headers = ResolveAddendum
    else:
        headers = FetchAddendum

        if cli_args.contents_in_report:
            headers = FetchAddendumWithBody

    return headers


def get_title(cli_args):
    if cli_args.action == "resolve":
        return "Resolving"

    return "Fetching"


@with_enricher_and_loading_bar(
    headers=get_headers,
    enricher_type="threadsafe",
    index_column="fetch_original_index",
    title=get_title,
    unit="urls",
    stats_sort_key=loading_bar_stats_sort_key,
)
@with_ctrl_c_warning
def action(cli_args, enricher: casanova.ThreadSafeEnricher, loading_bar):
    # Resolving or fetching?
    resolve = cli_args.action == "resolve"

    # HTTP method
    http_method = cli_args.method

    # Cookie grabber
    get_cookie = None
    if cli_args.grab_cookies:
        get_cookie = grab_cookies(cli_args.grab_cookies)

    # Global headers
    global_headers = None
    if cli_args.headers:
        global_headers = {}

        for header in cli_args.headers:
            k, v = parse_http_header(header)
            global_headers[k] = v

    if cli_args.column not in enricher.headers:
        raise InvalidArgumentsError(
            'Could not find the "%s" column containing the urls in the given CSV file.'
            % cli_args.column
        )

    url_pos = enricher.headers[cli_args.column]

    filename_pos = None

    if not resolve and cli_args.filename is not None:
        if cli_args.filename not in enricher.headers:
            raise InvalidArgumentsError(
                'Could not find the "%s" column containing the filenames in the given CSV file.'
                % cli_args.filename
            )

        filename_pos = enricher.headers[cli_args.filename]

    only_shortened = getattr(cli_args, "only_shortened", False)
    only_html = getattr(cli_args, "only_html", False)

    def url_key(item) -> Optional[str]:
        url = item[1][url_pos].strip()

        if not url:
            return

        if only_shortened and not is_shortened_url(url):
            return

        if only_html and not could_be_html(url):
            return

        # Url templating
        if cli_args.url_template:
            return cli_args.url_template.format(value=url)

        return url

    def request_args(payload: FetchWorkerPayload):
        cookie = None

        # Cookie
        if get_cookie:
            cookie = get_cookie(payload.url)

        # Headers
        headers = None

        if global_headers:
            headers = global_headers

        return {"method": http_method, "cookie": cookie, "headers": headers}

    # Worker callback internals
    filename_builder = None
    files_writer = None

    if not resolve:
        try:
            filename_builder = FilenameBuilder(
                folder_strategy=cli_args.folder_strategy,
                template=cli_args.filename_template,
            )
        except TypeError:
            raise FatalError(
                [
                    'Invalid "%s" --folder-strategy!' % cli_args.folder_strategy,
                    "Check the list at the end of the command help:",
                    "  $ minet fetch -h",
                ]
            )

        files_writer = ThreadSafeFilesWriter(cli_args.output_dir)

    def worker_callback(result: FetchResult[List]) -> None:
        if cli_args.dont_save:
            return

        # NOTE: at this point the callback is only fired on success
        assert result.response

        row = result.item[1]
        response = result.response

        if cli_args.keep_failed_contents and response.status != 200:
            return

        if cli_args.only_html and not response.is_html:
            return

        # First we need to build a filename
        filename_cell = row[filename_pos] if filename_pos is not None else None

        formatter_kwargs = {}

        if cli_args.filename_template and "line" in cli_args.filename_template:
            formatter_kwargs["line"] = enricher.wrap(row)

        try:
            assert filename_builder is not None

            filename = filename_builder(
                response.end_url,
                filename=filename_cell,
                ext=response.ext,
                formatter_kwargs=formatter_kwargs,
                compressed=cli_args.compress,
            )
        except FilenameFormattingError as e:
            result.error = e
            return

        response["filename"] = filename

        # Decoding the response data?
        data: Union[str, bytes] = response.body

        if response.is_text and (
            cli_args.standardize_encoding or cli_args.contents_in_report
        ):
            data = response.body.decode(response.likely_encoding, errors="replace")

            if cli_args.contents_in_report:
                response["decoded_contents"] = data

        # Writing the file?
        # TODO: specify what should happen when contents are empty (e.g. POST queries)
        if data and not cli_args.contents_in_report:
            assert files_writer is not None

            files_writer.write(filename, data, compress=cli_args.compress)

    common_executor_kwargs = {
        "insecure": cli_args.insecure,
        "max_workers": cli_args.threads,
        "wait": False,
        "daemonic": False,
    }
    common_imap_kwargs = {
        "key": url_key,
        "throttle": cli_args.throttle,
        "domain_parallelism": cli_args.domain_parallelism,
        "max_redirects": cli_args.max_redirects,
    }

    if cli_args.timeout is not None:
        common_executor_kwargs["timeout"] = cli_args.timeout

    # Normal fetch
    if not resolve:

        Addendum = (
            FetchAddendum if not cli_args.contents_in_report else FetchAddendumWithBody
        )

        with FetchThreadPoolExecutor(**common_executor_kwargs) as executor:
            for result in executor.imap_unordered(
                enricher,
                request_args=request_args,
                callback=worker_callback,
                **common_imap_kwargs
            ):
                with loading_bar.step():
                    index, row = result.item

                    if not result.url:
                        enricher.writerow(index, row)
                        loading_bar.inc_stat("filtered", style="warning")
                        continue

                    addendum = Addendum()

                    # No error
                    if result.error is None:
                        assert result.response is not None

                        response = result.response
                        status = response.status

                        loading_bar.inc_stat(status, style=get_style_for_status(status))

                        addendum.infos_from_response(response)
                        enricher.writerow(index, row, addendum)

                    # Handling potential errors
                    else:
                        error_code = report_error(result.error)

                        loading_bar.inc_stat(error_code, style="error")

                        resolved_url = None

                        if isinstance(result.error, InvalidURLError):
                            resolved_url = result.error.url

                        if isinstance(result.error, FilenameFormattingError):
                            loading_bar.print(
                                report_filename_formatting_error(result.error)
                            )

                        addendum.fetch_error = error_code
                        addendum.resolved_url = resolved_url

                        enricher.writerow(index, row, addendum)

    # Resolve
    else:

        with ResolveThreadPoolExecutor(**common_executor_kwargs) as executor:
            for result in executor.imap_unordered(
                enricher,
                resolve_args=request_args,
                follow_meta_refresh=cli_args.follow_meta_refresh,
                follow_js_relocation=cli_args.follow_js_relocation,
                infer_redirection=cli_args.infer_redirection,
                canonicalize=cli_args.canonicalize,
                **common_imap_kwargs
            ):
                with loading_bar.step():
                    index, row = result.item

                    if not result.url:
                        enricher.writerow(index, row)
                        loading_bar.inc_stat("filtered", style="warning")
                        continue

                    addendum = ResolveAddendum()

                    # No error
                    if result.error is None:
                        assert result.stack is not None

                        # Reporting in output
                        last = result.stack[-1]
                        status = last.status
                        loading_bar.inc_stat(status, style=get_style_for_status(status))

                        addendum.infos_from_stack(result.stack)
                        enricher.writerow(index, row, addendum)

                    # Handling potential errors
                    else:
                        error_code = report_error(result.error)
                        loading_bar.inc_stat(error_code, style="error")

                        addendum.resolution_error = error_code
                        enricher.writerow(index, row, addendum)
