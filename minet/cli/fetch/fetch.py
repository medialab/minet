# =============================================================================
# Minet Fetch CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and fetching the urls found
# in the given column. This is done in a respectful multithreaded fashion to
# optimize both running time & memory.
#
from typing import Optional, List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from minet.browser.threadsafe_browser import BrowserOrBrowserContext

import casanova
from casanova import TabularRecord
from dataclasses import dataclass
from datetime import datetime
from ural import is_shortened_url, could_be_html
from os.path import join as pathjoin

from minet.executors import (
    HTTPWorkerPayload,
    HTTPThreadPoolExecutor,
    BrowserThreadPoolExecutor,
    PassthroughRequestResult,
    SuccessfulRequestResult,
    PassthroughResolveResult,
    SuccessfulResolveResult,
)
from minet.fs import FilenameBuilder, ThreadSafeFileWriter
from minet.cookies import get_cookie_resolver_from_browser
from minet.headers import parse_http_header
from minet.web import (
    Response,
    RedirectionStack,
)
from minet.exceptions import InvalidURLError, FilenameFormattingError, HTTPCallbackError
from minet.heuristics import should_spoof_ua_when_resolving
from minet.cli.exceptions import InvalidArgumentsError
from minet.cli.reporters import report_filename_formatting_error
from minet.cli.loading_bar import LoadingBar
from minet.cli.utils import with_enricher_and_loading_bar, with_ctrl_c_warning


@dataclass
class WorkerCallbackResult:
    path: Optional[str] = None
    decoded_contents: Optional[str] = None


@dataclass
class FetchAddendum(TabularRecord):
    resolved_url: Optional[str] = None
    http_status: Optional[int] = None
    datetime_utc: Optional[datetime] = None
    fetch_error: Optional[str] = None
    path: Optional[str] = None
    mimetype: Optional[str] = None
    encoding: Optional[str] = None
    body_size: Optional[int] = None

    def infos_from_response(
        self, response: Response, callback_result: Optional[WorkerCallbackResult]
    ) -> None:
        self.resolved_url = response.end_url
        self.http_status = response.status
        self.datetime_utc = response.end_datetime
        self.path = callback_result.path if callback_result else None
        self.encoding = response.encoding
        self.mimetype = response.mimetype
        self.body_size = len(response)


@dataclass
class FetchAddendumWithBody(FetchAddendum):
    body: Optional[str] = None

    def infos_from_response(
        self, response: Response, callback_result: Optional[WorkerCallbackResult]
    ) -> None:
        super().infos_from_response(response, callback_result)
        self.body = callback_result.decoded_contents if callback_result else None


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
        self.http_status = last.status
        self.redirect_count = len(stack) - 1
        self.redirect_chain = [step.type for step in stack]


@dataclass
class ScreenshotAddendum(TabularRecord):
    http_status: Optional[int] = None
    screenshot_error: Optional[str] = None
    path: Optional[str] = None


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
        return ResolveAddendum

    if cli_args.action == "screenshot":
        return ScreenshotAddendum

    headers = FetchAddendum

    if cli_args.contents_in_report:
        headers = FetchAddendumWithBody

    return headers


def get_title(cli_args):
    if cli_args.action == "resolve":
        return "Resolving"

    if cli_args.action == "screenshot":
        return "Screenshotting"

    return "Fetching"


@with_enricher_and_loading_bar(
    headers=get_headers,
    enricher_type="threadsafe",
    index_column="original_index",
    title=get_title,
    unit="urls",
    stats_sort_key=loading_bar_stats_sort_key,
)
@with_ctrl_c_warning
def action(cli_args, enricher: casanova.ThreadSafeEnricher, loading_bar: LoadingBar):
    # Resolving or fetching?
    resolve = cli_args.action == "resolve"

    # HTTP method
    http_method = getattr(cli_args, "method", None)

    # Cookie grabber
    get_cookie = None

    if getattr(cli_args, "grab_cookies", False):
        get_cookie = get_cookie_resolver_from_browser(cli_args.grab_cookies)

    # Global headers
    global_headers = None

    if getattr(cli_args, "headers", None):
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

    if not resolve and cli_args.filename_column is not None:
        if cli_args.filename_column not in enricher.headers:
            raise InvalidArgumentsError(
                'Could not find the "%s" column containing the filenames in the given CSV file.'
                % cli_args.filename_column
            )

        filename_pos = enricher.headers[cli_args.filename_column]

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

    def request_args(payload: HTTPWorkerPayload):
        cookie = None

        # Cookie
        if get_cookie:
            cookie = get_cookie(payload.url)

        # Headers
        headers = None

        if global_headers:
            headers = global_headers

        spoof_ua = cli_args.spoof_user_agent

        if not spoof_ua and resolve:
            spoof_ua = should_spoof_ua_when_resolving(payload.domain)

        return {
            "method": http_method,
            "cookie": cookie,
            "headers": headers,
            "spoof_ua": spoof_ua,
        }

    # Worker callback internals
    filename_builder = None
    file_writer = None

    if not resolve:
        filename_builder = FilenameBuilder(
            folder_strategy=cli_args.folder_strategy,
            template=cli_args.filename_template,
        )

        file_writer = ThreadSafeFileWriter(
            cli_args.output_dir, sqlar=getattr(cli_args, "sqlar", False)
        )

    def worker_callback(
        item, url: str, response: Response
    ) -> Optional[WorkerCallbackResult]:
        if cli_args.dont_save:
            return

        row = item[1]

        if cli_args.keep_failed_contents and response.status != 200:
            return

        if cli_args.only_html and not response.is_html:
            return

        addendum = WorkerCallbackResult()

        # First we need to build a filename
        filename_cell = row[filename_pos] if filename_pos is not None else None

        formatter_kwargs = {}

        if cli_args.filename_template and "row" in cli_args.filename_template:
            formatter_kwargs["row"] = enricher.wrap(row)

        assert filename_builder is not None

        filename = filename_builder(
            response.end_url,
            filename=filename_cell,
            ext=response.ext,
            formatter_kwargs=formatter_kwargs,
            compressed=cli_args.compress_on_disk,
        )

        addendum.path = filename

        # Decoding the response data?
        data: Union[str, bytes] = response.body

        if response.is_text and (
            cli_args.standardize_encoding or cli_args.contents_in_report
        ):
            data = response.body.decode(response.likely_encoding, errors="replace")

            if cli_args.contents_in_report:
                addendum.decoded_contents = data

        # Writing the file?
        # TODO: specify what should happen when contents are empty (e.g. POST queries)
        if data and not cli_args.contents_in_report:
            assert file_writer is not None

            file_writer.write(filename, data, compress=cli_args.compress_on_disk)

        return addendum

    common_executor_kwargs = {
        "max_workers": cli_args.threads,
        "wait": False,
        "daemonic": False,
    }
    common_http_executor_kwargs = {
        **common_executor_kwargs,
        "insecure": getattr(cli_args, "insecure", None),
        "proxy": getattr(cli_args, "proxy", None),
    }

    retries = getattr(cli_args, "retries", 0)

    if retries:
        common_http_executor_kwargs["retry"] = True
        common_http_executor_kwargs["retryer_kwargs"] = {
            "retry_on_timeout": True,
            "max_attempts": 1 + retries,
        }

    common_imap_kwargs = {
        "key": url_key,
        "throttle": cli_args.throttle,
        "domain_parallelism": cli_args.domain_parallelism,
    }
    common_http_imap_kwargs = {
        **common_imap_kwargs,
        "max_redirects": getattr(cli_args, "max_redirects", None),
    }

    if cli_args.timeout is not None:
        common_http_executor_kwargs["timeout"] = cli_args.timeout

    # Normal fetch
    if cli_args.action == "fetch":
        Addendum = (
            FetchAddendum if not cli_args.contents_in_report else FetchAddendumWithBody
        )

        with HTTPThreadPoolExecutor(**common_http_executor_kwargs) as executor:
            loading_bar.append_to_title(" (t=%i)" % executor.max_workers)

            for result, callback_result in executor.request(
                enricher,
                request_args=request_args,
                callback=worker_callback,
                passthrough=True,
                use_pycurl=cli_args.pycurl,
                compressed=cli_args.compress_transfer,
                **common_http_imap_kwargs
            ):
                with loading_bar.step():
                    index, row = result.item

                    if isinstance(result, PassthroughRequestResult):
                        enricher.writerow(index, row)
                        loading_bar.inc_stat("filtered", style="warning")
                        continue

                    addendum = Addendum()

                    # No error
                    if isinstance(result, SuccessfulRequestResult):
                        response = result.response
                        status = response.status

                        loading_bar.inc_stat(
                            str(status), style=get_style_for_status(status)
                        )

                        addendum.infos_from_response(response, callback_result)
                        enricher.writerow(index, row, addendum)

                    # Handling potential errors
                    else:
                        error = result.error

                        if isinstance(error, HTTPCallbackError):
                            error.unwrap(FilenameFormattingError)

                        loading_bar.inc_stat(result.error_code, style="error")

                        resolved_url = None

                        if isinstance(error, InvalidURLError):
                            resolved_url = error.url

                        if isinstance(error, FilenameFormattingError):
                            loading_bar.print(report_filename_formatting_error(error))

                        addendum.fetch_error = result.error_code
                        addendum.resolved_url = resolved_url

                        enricher.writerow(index, row, addendum)

    # Resolve
    elif cli_args.action == "resolve":
        with HTTPThreadPoolExecutor(**common_http_executor_kwargs) as executor:
            loading_bar.append_to_title("(t=%i)" % executor.max_workers)

            for result in executor.resolve(
                enricher,
                resolve_args=request_args,
                follow_meta_refresh=cli_args.follow_meta_refresh,
                follow_js_relocation=cli_args.follow_js_relocation,
                infer_redirection=cli_args.infer_redirection,
                canonicalize=cli_args.canonicalize,
                passthrough=True,
                **common_http_imap_kwargs
            ):
                with loading_bar.step():
                    index, row = result.item

                    if isinstance(result, PassthroughResolveResult):
                        enricher.writerow(index, row)
                        loading_bar.inc_stat("filtered", style="warning")
                        continue

                    addendum = ResolveAddendum()

                    # No error
                    if isinstance(result, SuccessfulResolveResult):
                        # Reporting in output
                        last = result.stack[-1]
                        status = last.status

                        # Status can be None with inference etc.
                        if status is not None:
                            loading_bar.inc_stat(
                                str(status), style=get_style_for_status(status)
                            )

                        addendum.infos_from_stack(result.stack)
                        enricher.writerow(index, row, addendum)

                    # Handling potential errors
                    else:
                        loading_bar.inc_stat(result.error_code, style="error")

                        addendum.resolution_error = result.error_code
                        enricher.writerow(index, row, addendum)

    # Screenshot
    elif cli_args.action == "screenshot":
        import asyncio
        from playwright.async_api import (
            Error as PlaywrightError,
            TimeoutError as PlaywrightTimeoutError,
        )

        from minet.browser.utils import convert_playwright_error
        from minet.exceptions import BrowserUnknownError
        from minet.serialization import serialize_error_as_slug

        goto_timeout = int(
            (cli_args.timeout if cli_args.timeout is not None else 30) * 1000
        )

        async def screenshot(
            context: "BrowserOrBrowserContext", payload: HTTPWorkerPayload
        ) -> ScreenshotAddendum:
            async with await context.new_page() as page:
                try:
                    response = await page.goto(
                        payload.url,
                        timeout=goto_timeout,
                        wait_until=cli_args.wait_until,
                    )
                except (PlaywrightError, PlaywrightTimeoutError) as e:
                    error = convert_playwright_error(e)

                    if isinstance(error, BrowserUnknownError):
                        raise e

                    return ScreenshotAddendum(
                        screenshot_error=serialize_error_as_slug(error)
                    )

                assert response is not None

                row = payload.item[1]
                filename = None

                if response.status == 200:
                    filename_cell = (
                        row[filename_pos] if filename_pos is not None else None
                    )

                    formatter_kwargs = {}

                    if (
                        cli_args.filename_template
                        and "row" in cli_args.filename_template
                    ):
                        formatter_kwargs["row"] = enricher.wrap(row)

                    assert filename_builder is not None

                    filename = filename_builder(
                        page.url,
                        filename=filename_cell,
                        ext=".png",
                        formatter_kwargs=formatter_kwargs,
                    )

                    if cli_args.wait is not None:
                        await asyncio.sleep(cli_args.wait)

                    await page.screenshot(
                        path=pathjoin(cli_args.output_dir, filename),
                        full_page=cli_args.full_page,
                    )

                return ScreenshotAddendum(
                    http_status=response.status,
                    screenshot_error=None,
                    path=filename,
                )

        with BrowserThreadPoolExecutor(
            width=cli_args.width,
            height=cli_args.height,
            adblock=cli_args.adblock,
            automatic_consent=cli_args.automatic_consent,
            **common_executor_kwargs
        ) as executor:
            loading_bar.append_to_title(" (t=%i)" % executor.max_workers)

            for result in executor.run(
                enricher, screenshot, passthrough=True, **common_imap_kwargs
            ):
                with loading_bar.step():
                    (index, row), addendum = result

                    if addendum:
                        if addendum.screenshot_error is not None:
                            loading_bar.inc_stat(
                                addendum.screenshot_error, style="error"
                            )
                        elif addendum.http_status:
                            loading_bar.inc_stat(
                                str(addendum.http_status),
                                style=get_style_for_status(addendum.http_status),
                            )

                    enricher.writerow(index, row, addendum)

    else:
        raise NotImplementedError
