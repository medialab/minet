from typing import Callable, Optional
from minet.types import Literal

import asyncio
import platform
from threading import Thread, Event
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

from minet.__future__.threaded_child_watcher import ThreadedChildWatcher
from minet.browser.plawright_shim import run_playwright
from minet.browser.utils import PageContextManager, BrowserContextContextManager

UNIX = "windows" not in platform.system().lower()
LTE_PY37 = platform.python_version_tuple()[:2] <= ("3", "7")
SUPPORTED_BROWSERS = ("chromium", "firefox")


BrowserName = Literal["chromium", "firefox"]

# TODO: contexts, persistent contexts etc.


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

        # NOTE: forcing the executable path so this works with pyinstaller
        self.browser = await browser_type.launch(
            headless=True, executable_path=browser_type.executable_path
        )

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

    async def __call_with_new_page(
        self, url: Optional[str], fn: Callable, *args, **kwargs
    ):
        context = await self.browser.new_context()

        async with BrowserContextContextManager(context):
            page = await self.browser.new_page()

            if self.stealthy:
                await stealth_async(page)

            async with PageContextManager(page):
                if url is not None:
                    await page.goto(url)
                return await fn(page, *args, **kwargs)

    def run_with_page(self, fn: Callable, *args, url: Optional[str] = None, **kwargs):
        future = asyncio.run_coroutine_threadsafe(
            self.__call_with_new_page(url, fn, *args, **kwargs), self.loop
        )

        return future.result()
