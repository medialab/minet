from typing import Callable, TypeVar, Awaitable, Set
from minet.types import Literal, Concatenate, ParamSpec

import os
import asyncio
import platform
from concurrent.futures import Future
from os.path import expanduser
from threading import Thread, Event, Lock
from playwright.async_api import async_playwright, Page, Browser

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
