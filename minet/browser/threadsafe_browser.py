from typing import Callable, TypeVar, Awaitable, Set, Optional, Union, Literal
from minet.types import Concatenate, ParamSpec

import os
import asyncio
from shutil import rmtree
from concurrent.futures import Future
from threading import Thread, Event, Lock
from playwright.async_api import async_playwright, Browser, BrowserContext
from urllib3._collections import HTTPHeaderDict

from minet.exceptions import UnknownBrowserError
from minet.web import Response
from minet.browser.plawright_shim import install_browser
from minet.browser.utils import get_browsers_path, get_temp_persistent_context_path
from minet.browser.extensions import get_extension_path, ensure_extension_is_downloaded
from minet.types import Redirection

SUPPORTED_BROWSERS = ("chromium", "firefox")


BrowserName = Literal["chromium", "firefox"]
T = TypeVar("T")
P = ParamSpec("P")
BrowserOrBrowserContext = Union[Browser, BrowserContext]
BrowserCallable = Callable[Concatenate[Browser, P], Awaitable[T]]
BrowserContextCallable = Callable[Concatenate[BrowserContext, P], Awaitable[T]]
BrowserOrBrowserContextCallable = Callable[
    Concatenate[BrowserOrBrowserContext, P], Awaitable[T]
]

# TODO: introduce stealth back
# TODO: abstract screenshot function
# TODO: helper for stealth page, monkey patch some function?


class ThreadsafeBrowser:
    def __init__(
        self,
        browser: BrowserName = "chromium",
        headless: bool = True,
        automatic_consent: bool = False,
        adblock: bool = False,
        width: int = 1920,
        height: int = 1080,
    ) -> None:
        if browser not in SUPPORTED_BROWSERS:
            raise UnknownBrowserError(browser)

        self.extensions = []

        if automatic_consent:
            self.extensions.append("i-still-dont-care-about-cookies")

        if adblock:
            self.extensions.append("ublock-origin")

        # NOTE: doing this in constructor to avoid threading issues down the line
        for ext in self.extensions:
            ensure_extension_is_downloaded(ext)

        self.requires_extensions = bool(self.extensions)
        self.persistent_user_data_dir = None
        self.persistent = self.requires_extensions

        if self.requires_extensions and browser != "chromium":
            raise TypeError("adblock and automatic_consent only work with chromium")

        self.browser_name: str = browser
        self.browser: Optional[Browser] = None
        self.default_browser_context: Optional[BrowserContext] = None
        self.headless = headless
        self.width = width
        self.height = height

        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", get_browsers_path())

        install_browser(self.browser_name)

        self.loop = asyncio.new_event_loop()
        self.start_event = Event()
        self.thread = Thread(
            name="Thread-browser-%i" % id(self), target=self.__thread_worker
        )

        self.running_futures: Set[Future] = set()
        self.running_futures_lock = Lock()

        # Starting loop thread
        self.thread.start()
        self.start_event.wait()

    async def __start_playwright(self) -> None:
        self.playwright = await async_playwright().start()

        if self.browser_name == "chromium":
            browser_type = self.playwright.chromium
        elif self.browser_name == "firefox":
            browser_type = self.playwright.firefox
        else:
            raise TypeError("unsupported browser")

        if self.requires_extensions:
            args = []
            disable_extensions_except = []

            for ext in self.extensions:
                p = get_extension_path(ext)
                disable_extensions_except.append(p)
                args.append(f"--load-extension={p}")

            args.append(
                f"--disable-extensions-except={','.join(disable_extensions_except)}"
            )

            if self.headless:
                args.append("--headless=new")

            user_data_dir = get_temp_persistent_context_path()
            rmtree(user_data_dir, ignore_errors=True)
            self.persistent_user_data_dir = user_data_dir

            self.default_browser_context = await browser_type.launch_persistent_context(
                user_data_dir,
                headless=False,
                args=args,
                viewport={"width": self.width, "height": self.height},
                locale="en-US",
            )

        else:
            self.browser = await browser_type.launch(headless=self.headless)
            self.default_browser_context = await self.browser.new_context(
                viewport={"width": self.width, "height": self.height}, locale="en-US"
            )

    async def __stop_playwright(self) -> None:
        # NOTE: we need to make sure those were actually launched, in
        # case of a nasty race condition

        if self.default_browser_context is not None:
            await self.default_browser_context.close()

        if self.browser is not None:
            await self.browser.close()

        # NOTE: this hangs without the proper child watcher
        await self.playwright.stop()

    def stop(self) -> None:
        # NOTE: if we don't do this and some job sent
        # to a threadpool executor raises and triggers
        # the closing of the playwright driver, then a
        # catastrophic chain reaction of exception will
        # make some jobs hang up and block indefinitely
        # which will cause a deadlock.
        with self.running_futures_lock:
            for fut in self.running_futures:
                if not fut.done():
                    fut.cancel()

        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()

    def __thread_worker(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.__start_playwright())
        self.start_event.set()

        # NOTE: we are now ready to accept tasks
        try:
            self.loop.run_forever()
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())

        self.loop.run_until_complete(self.__stop_playwright())

    def __handle_future(self, future: Future):
        with self.running_futures_lock:
            self.running_futures.add(future)

        try:
            return future.result()
        finally:
            with self.running_futures_lock:
                self.running_futures.remove(future)

    def run(self, fn: BrowserCallable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        if self.browser is None:
            raise TypeError("cannot run browser-level callable with persistent context")

        future = asyncio.run_coroutine_threadsafe(
            fn(self.browser, *args, **kwargs), self.loop
        )

        return self.__handle_future(future)

    def run_in_default_context(
        self, fn: BrowserContextCallable[P, T], *args: P.args, **kwargs: P.kwargs
    ) -> T:
        assert self.default_browser_context is not None

        future = asyncio.run_coroutine_threadsafe(
            fn(self.default_browser_context, *args, **kwargs), self.loop
        )

        return self.__handle_future(future)

    def run_in_browser_or_default_context(
        self,
        fn: BrowserOrBrowserContextCallable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        target = self.browser

        if target is None:
            target = self.default_browser_context

        assert target is not None

        future = asyncio.run_coroutine_threadsafe(
            fn(target, *args, **kwargs), self.loop
        )

        return self.__handle_future(future)

    async def __request(self, context: BrowserContext, url: str) -> Response:
        async with await context.new_page() as page:
            emulated_response = await page.goto(url)

            assert emulated_response is not None

            headers = HTTPHeaderDict()

            for header in await emulated_response.headers_array():
                headers[header["name"]] = header["value"]

            response = Response(
                url,
                [Redirection(url, status=emulated_response.status)],
                headers,
                emulated_response.status,
                (await page.content()).encode(),
                known_encoding="utf-8",
            )

            return response

    def request(self, url: str) -> Response:
        return self.run_in_default_context(self.__request, url)
