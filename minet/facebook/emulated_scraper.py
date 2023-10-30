import re
import json
from playwright.async_api import BrowserContext, Response, TimeoutError
from playwright_stealth import stealth_async

from minet.browser import ThreadsafeBrowser
from minet.browser.utils import try_expect_response


VIEW_MORE_COMMENTS_RE = re.compile(r"View\s+.+more\s+comments?", re.I)
VIEW_MORE_REPLIES_RE = re.compile(r"View\s+.+more\s+replies", re.I)


def is_graphql_comments_response(response: Response) -> bool:
    if "/api/graphql/" not in response.url:
        return False

    return (
        response.request.headers.get("x-fb-friendly-name")
        == "CometUFICommentsProviderForDisplayCommentsQuery"
    )


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

            async def expect_comments(action):
                response = await try_expect_response(
                    page, action, is_graphql_comments_response
                )

                return await response.json()

            async def select_all_comments():
                await page.get_by_text("Most relevant").first.click()
                await page.get_by_text("All comments").first.click()

            async def view_more_replies():
                await page.get_by_text(VIEW_MORE_REPLIES_RE).first.click(timeout=3000)

            async def view_more_comments():
                await page.get_by_text(VIEW_MORE_COMMENTS_RE).first.click(timeout=3000)

            # comments = []

            data = await expect_comments(select_all_comments)

            while True:
                await page.wait_for_timeout(1000)

                try:
                    data = await expect_comments(view_more_comments)
                except TimeoutError:
                    break

            while True:
                await page.wait_for_timeout(1000)

                try:
                    data = await expect_comments(view_more_replies)
                except TimeoutError:
                    break

            with open("./dump.json", "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            await page.wait_for_timeout(1000000)

    def scrape_comments(self, url: str):
        self.browser.run_in_default_context(self.__scrape_comments, url)
