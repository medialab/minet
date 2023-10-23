from typing import Callable, TypeVar, Awaitable, Set
from minet.types import Literal, Concatenate, ParamSpec

import os
import asyncio
import platform
from shutil import rmtree
from concurrent.futures import Future
from threading import Thread, Event, Lock
from playwright.async_api import async_playwright, Browser

from minet.__future__.threaded_child_watcher import ThreadedChildWatcher
from minet.exceptions import UnknownBrowserError
from minet.browser.plawright_shim import run_playwright
from minet.browser.utils import get_browsers_path, get_temp_persistent_context_path
from minet.browser.extensions import get_extension_path, ensure_extension_is_downloaded

UNIX = "windows" not in platform.system().lower()
LTE_PY37 = platform.python_version_tuple()[:2] <= ("3", "7")
SUPPORTED_BROWSERS = ("chromium", "firefox")


BrowserName = Literal["chromium", "firefox"]
T = TypeVar("T")
P = ParamSpec("P")
BrowserCallable = Callable[Concatenate[Browser, P], Awaitable[T]]

# TODO: introduce stealth back
# TODO: abstract screenshot function


class ThreadsafeBrowser:
    def __init__(
        self,
        browser: BrowserName = "chromium",
        automatic_consent: bool = False,
        adblock: bool = False,
    ) -> None:
        if browser not in SUPPORTED_BROWSERS:
            raise UnknownBrowserError(browser)

        self.extensions = []

        if automatic_consent:
            self.extensions.append("i-still-dont-care-about-cookies")

        if adblock:
            self.extensions.append("ublock-origin")

        self.requires_extensions = bool(self.extensions)

        if self.requires_extensions and browser != "chromium":
            raise TypeError("adblock and automatic_consent only work with chromium")

        # NOTE: on unix python 3.7, child watching does not
        # work properly when asyncio is not running from the main thread
        if UNIX and LTE_PY37:
            asyncio.set_child_watcher(ThreadedChildWatcher())

        self.browser_name = browser

        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", get_browsers_path())

        run_playwright("install", self.browser_name)

        self.loop = asyncio.new_event_loop()
        self.start_event = Event()
        self.thread = Thread(target=self.__thread_worker)

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
                ensure_extension_is_downloaded(ext)

                p = get_extension_path(ext)
                disable_extensions_except.append(p)
                args.append(f"--load-extension={p}")

            args.append(
                f"--disable-extensions-except={','.join(disable_extensions_except)}"
            )

            user_data_dir = get_temp_persistent_context_path()
            rmtree(user_data_dir, ignore_errors=True)

            # TODO: so now there is an issue because we are returning a
            # context, not a browser
            self.browser = await browser_type.launch_persistent_context(
                user_data_dir,
                headless=False,
                args=args,
            )

        else:
            self.browser = await browser_type.launch(headless=True)

    async def __stop_playwright(self) -> None:
        # NOTE: we need to make sure those were actually launched, in
        # case of a nasty race condition
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

    async def __call(self, fn: Callable, *args, **kwargs):
        return await fn(self.browser, *args, **kwargs)

    def run(self, fn: BrowserCallable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        future = asyncio.run_coroutine_threadsafe(
            self.__call(fn, *args, **kwargs), self.loop
        )

        with self.running_futures_lock:
            self.running_futures.add(future)

        try:
            return future.result()
        finally:
            with self.running_futures_lock:
                self.running_futures.remove(future)
