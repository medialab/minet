from typing import Callable, Optional, TypeVar, Awaitable
from minet.types import Literal, Concatenate, ParamSpec

import os
import asyncio
import platform
from os.path import expanduser
from threading import Thread, Event
from playwright.async_api import async_playwright, Page, Browser
from playwright_stealth import stealth_async

from minet.__future__.threaded_child_watcher import ThreadedChildWatcher
from minet.browser.plawright_shim import run_playwright

UNIX = "windows" not in platform.system().lower()
LTE_PY37 = platform.python_version_tuple()[:2] <= ("3", "7")
SUPPORTED_BROWSERS = ("chromium", "firefox")


BrowserName = Literal["chromium", "firefox"]
T = TypeVar("T")
P = ParamSpec("P")
PageCallable = Callable[Concatenate[Page, P], Awaitable[T]]
BrowserCallable = Callable[Concatenate[Browser, P], Awaitable[T]]

# TODO: launch with persistent context


class ThreadsafeBrowser:
    def __init__(
        self,
        browser: BrowserName = "chromium",
        stealthy: bool = False,
    ) -> None:
        if browser not in SUPPORTED_BROWSERS:
            raise TypeError("unsupported browser")

        # NOTE: on unix python 3.7, child watching does not
        # work properly when asyncio is not running from the main thread
        if UNIX and LTE_PY37:
            asyncio.set_child_watcher(ThreadedChildWatcher())

        self.stealthy = stealthy
        self.browser_name = browser

        os.environ.setdefault(
            "PLAYWRIGHT_BROWSERS_PATH", expanduser("~/.minet-browsers")
        )

        run_playwright("install", self.browser_name)

        self.loop = asyncio.new_event_loop()
        self.start_event = Event()
        self.thread = Thread(target=self.__thread_worker)

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

        # TODO: we need to find a way to force frozen executable to use the same
        # directory as non-frozen one, e.g. by mangling PLAYWRIGHT_BROWSERS_PATH
        # or sys.frozen
        self.browser = await browser_type.launch(headless=True)

    async def __stop_playwright(self) -> None:
        # NOTE: we need to make sure those were actually launched, in
        # case of a nasty race condition
        await self.browser.close()

        # NOTE: this hangs without the proper child watcher
        await self.playwright.stop()

    def stop(self) -> None:
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

    async def __call_with_new_page(
        self, fn: Callable, *args, url: Optional[str] = None, **kwargs
    ):
        async with await self.browser.new_context() as context:
            async with await context.new_page() as page:
                if self.stealthy:
                    await stealth_async(page)

                if url is not None:
                    await page.goto(url)
                return await fn(page, *args, **kwargs)

    def run(self, fn: BrowserCallable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        future = asyncio.run_coroutine_threadsafe(
            self.__call(fn, *args, **kwargs), self.loop
        )

        return future.result()

    def run_with_new_page(
        self,
        fn: PageCallable[P, T],
        url: Optional[str] = None,
        *args: P.args,
        **kwargs: P.kwargs
    ) -> T:
        future = asyncio.run_coroutine_threadsafe(
            self.__call_with_new_page(fn, *args, url=url, **kwargs), self.loop
        )

        return future.result()
