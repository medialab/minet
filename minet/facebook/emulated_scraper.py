from typing import Callable, Awaitable

import re
import json
import asyncio
from playwright.async_api import BrowserContext, Response, Page, TimeoutError
from playwright_stealth import stealth_async

from minet.browser import ThreadsafeBrowser


VIEW_MORE_COMMENTS_RE = re.compile(r"View\s+.+more\s+comments?", re.I)
VIEW_MORE_REPLIES_RE = re.compile(r"(?:View\s+.+more\s+replies|\d+\s+replies)", re.I)


def is_graphql_comments_response(response: Response) -> bool:
    if "/api/graphql/" not in response.url:
        return False

    return (
        response.request.headers.get("x-fb-friendly-name")
        == "CometUFICommentsProviderForDisplayCommentsQuery"
    )


async def expect_comments(page: Page, fn: Callable[[], Awaitable[None]]):
    async with page.expect_response(is_graphql_comments_response) as response_catcher:
        try:
            await fn()
        except TimeoutError:
            print("timeout")
            return None

    response = await response_catcher.value
    data = await response.json()

    return data


class FacebookEmulatedScraper:
    def __init__(self):
        self.browser = ThreadsafeBrowser(headless=False, width=1024, height=768)

    def __enter__(self):
        return self

    def stop(self) -> None:
        self.browser.stop()

    def __exit__(self, *args):
        self.stop()

    async def __scrape_comments(self, context: BrowserContext, url: str):
        async with await context.new_page() as page:
            await stealth_async(page)

            await page.goto(url)
            await page.get_by_label("Decline optional cookies").first.click()
            await page.get_by_label("Close").first.click()

            # NOTE: this is only needed for debug
            await page.evaluate(
                """
                () => {
                    document.querySelector('[data-nosnippet]').remove();
                }
                """
            )

            async def select_all_comments():
                await page.get_by_text("Most relevant").first.click()
                await page.get_by_text("All comments").first.click()

            async def view_more_replies():
                await page.get_by_text(VIEW_MORE_REPLIES_RE).first.click(timeout=3)

            async def view_more_comments():
                await page.get_by_text(VIEW_MORE_COMMENTS_RE).click(timeout=10)

            data = await expect_comments(page, select_all_comments)

            # while True:
            #     await asyncio.sleep(1)
            #     data = await expect_comments(page, view_more_replies)

            #     if data is None:
            #         break

            while True:
                # await asyncio.sleep(1)
                data = await expect_comments(page, view_more_comments)

                if data is None:
                    break

            # TODO: View x more replies, View x more comments

            await asyncio.sleep(1000000)

            with open("./dump.json", "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def scrape_comments(self, url: str):
        self.browser.run_in_default_context(self.__scrape_comments, url)
