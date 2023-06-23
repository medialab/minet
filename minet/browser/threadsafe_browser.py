from typing import Callable, Optional

import asyncio
import platform
from threading import Thread, Event
from playwright.async_api import async_playwright, Page

from minet.__future__.threaded_child_watcher import ThreadedChildWatcher

UNIX = "windows" not in platform.system().lower()
LTE_PY37 = platform.python_version_tuple()[:2] <= ("3", "7")


class PageContext:
    def __init__(self, page: Page):
        self.page = page

    async def __aenter__(self) -> Page:
        return self.page

    async def __aexit__(self, *args):
        await self.page.close()


class ThreadsafeBrowser:
    def __init__(self) -> None:
        # NOTE: on unix python 3.7, child watching does not
        # work properly when asyncio is not running from the main thread
        if UNIX and LTE_PY37:
            asyncio.set_child_watcher(ThreadedChildWatcher())

        self.loop = asyncio.new_event_loop()
        self.start_event = Event()
        self.thread = Thread(target=self.__thread_worker)

        # Starting loop thread
        self.thread.start()
        self.start_event.wait()

    async def __start_playwright(self) -> None:
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)

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

    async def __call_within_new_page_context(
        self, url: Optional[str], fn: Callable, *args, **kwargs
    ):
        page = await self.browser.new_page()

        async with PageContext(page):
            if url is not None:
                await page.goto(url)
            return await fn(page, *args, **kwargs)

    def with_new_page(self, url: Optional[str], fn: Callable, *args, **kwargs):
        future = asyncio.run_coroutine_threadsafe(
            self.__call_within_new_page_context(url, fn, *args, **kwargs), self.loop
        )

        return future.result()
