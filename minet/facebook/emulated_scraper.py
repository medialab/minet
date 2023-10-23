from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import BrowserContext

import asyncio

from minet.browser import ThreadsafeBrowser


class FacebookEmulatedScraper:
    def __init__(self):
        self.browser = ThreadsafeBrowser(headless=False)

    def __enter__(self):
        return self

    def stop(self) -> None:
        self.browser.stop()

    def __exit__(self, *args):
        self.stop()

    async def __scrape_comments(self, context: "BrowserContext", url: str):
        async with await context.new_page() as page:
            await page.goto(url)
            await page.get_by_label("Decline optional cookies").first.click()
            await page.get_by_label("Close").first.click()
            await page.get_by_text("Most relevant").first.click()
            await page.get_by_text("All comments").first.click()

            await asyncio.sleep(60)

    def scrape_comments(self, url: str):
        self.browser.run_in_default_context(self.__scrape_comments, url)
