import asyncio
from playwright.async_api import async_playwright
from quenouille import imap_unordered
from threading import Thread, Event, current_thread
from ftest.thread_child_watcher import ThreadedChildWatcher

asyncio.set_child_watcher(ThreadedChildWatcher())

# ref: https://github.com/microsoft/playwright-python/issues/342
# ref: https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/registry/index.ts

URLS = [
    "https://www.lemonde.fr/",
    "https://lefigaro.fr",
    "https://liberation.fr",
    "https://mediapart.fr",
]


class ThreadsafePlaywrightBrowser:
    def __init__(self) -> None:
        self.loop = asyncio.new_event_loop()
        self.start_event = Event()
        self.thread = Thread(target=self.worker)

        # NOTE: can be wrapped
        self.thread.start()
        self.start_event.wait()

    async def start_playwright(self) -> None:
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)

    async def stop_playwright(self) -> None:
        # NOTE: we need to make sure those were actually launched...
        print(self.browser, self.playwright)
        await self.browser.close()
        print("browser closed")
        # NOTE: we need py3.8 for this to make sense unfortunately
        await self.playwright.stop()
        print("playwright closed")

    def stop(self) -> None:
        # tasks = asyncio.all_tasks(self.loop)
        # print(tasks)
        # NOTE: need to cancel ongoing tasks probably
        # future = asyncio.run_coroutine_threadsafe(self.stop_playwright(), self.loop)
        # future.result()
        self.loop.call_soon_threadsafe(self.loop.stop)
        print("joining", current_thread())
        self.thread.join()

    def worker(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start_playwright())
        self.start_event.set()
        try:
            self.loop.run_forever()
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        print("finished looping forever", current_thread())
        self.loop.run_until_complete(self.stop_playwright())

    async def get_page_title(self, url: str) -> str:
        page = await self.browser.new_page()
        await page.goto(url)

        title = await page.title()

        await page.close()

        return title

    def get_page_title_sync(self, url: str) -> str:
        return asyncio.run_coroutine_threadsafe(
            self.get_page_title(url), self.loop
        ).result()


browser = ThreadsafePlaywrightBrowser()
# print(browser.get_page_title_sync(URLS[0]))

for title in imap_unordered(
    [URLS[0]] * 5, lambda url: browser.get_page_title_sync(url), 5
):
    print(title)

browser.stop()


# async def main():
#     loop = asyncio.get_event_loop()

#     async with async_playwright() as playwright:
#         browser = await playwright.chromium.launch(
#             headless=True, timeout=5000, args=["--remote-debugging-port=9222"]
#         )

#         connection = await playwright.chromium.connect_over_cdp("http://localhost:9222")
#         page = await connection.new_page()
#         await page.goto("https://lemonde.fr")
#         print(await page.title())
#         await connection.close()
#         print(connection)
#         raise RuntimeError

#         async def get_page_title(url: str) -> str:
#             page = await browser.new_page()
#             await page.goto(url)

#             title = await page.title()

#             await page.close()

#             return title

#         def worker(url: str) -> str:
#             future = asyncio.run_coroutine_threadsafe(get_page_title(url), loop)
#             return future.result()

#         for result in imap_unordered(URLS, worker, 3):
#             print(result)

#         # for url in URLS:
#         #     print(url)
#         #     print(await get_page_title(url))

#         await browser.close()


# asyncio.run(main())
