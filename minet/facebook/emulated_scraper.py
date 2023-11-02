from typing import List

import re
from playwright.async_api import BrowserContext, Response, TimeoutError
from playwright_stealth import stealth_async
from ural.facebook import has_facebook_comments

from minet.browser import ThreadsafeBrowser
from minet.browser.utils import try_expect_response

from minet.facebook.exceptions import FacebookInvalidTargetError
from minet.facebook.types import FacebookComment


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
    def __init__(self, headless=True):
        self.browser = ThreadsafeBrowser(headless=headless, width=1024, height=768)

    def __enter__(self):
        return self

    def stop(self) -> None:
        self.browser.stop()

    def __exit__(self, *args):
        self.stop()

    async def __scrape_comments(
        self, context: BrowserContext, url: str
    ) -> List[FacebookComment]:
        async with await context.new_page() as page:
            await stealth_async(page)

            await page.goto(url)
            await page.get_by_label("Decline optional cookies").first.click()
            await page.get_by_label("Close").first.click()

            # NOTE: this is only needed for debug
            if not self.browser.headless:
                await page.evaluate(
                    """
                    () => {
                        document.querySelector('[data-nosnippet]').remove();
                    }
                    """
                )

            async def expect_comments(action) -> List[FacebookComment]:
                response = await try_expect_response(
                    page, action, is_graphql_comments_response
                )

                payload = await response.json()

                # with open("./dump.json", "w") as f:
                #     import json

                #     json.dump(payload, f, ensure_ascii=False, indent=2)

                return FacebookComment.from_payload(payload)

            async def select_all_comments():
                await page.get_by_text("Most relevant").first.click()
                await page.get_by_text("All comments").first.click()

            async def view_more_replies():
                await page.get_by_text(VIEW_MORE_REPLIES_RE).first.click(timeout=3000)

            async def view_more_comments():
                await page.get_by_text(VIEW_MORE_COMMENTS_RE).first.click(timeout=3000)

            comments: List[FacebookComment] = []

            comments.extend(await expect_comments(select_all_comments))

            # Deploying comments
            while True:
                await page.wait_for_timeout(1000)

                try:
                    comments.extend(await expect_comments(view_more_comments))
                except TimeoutError:
                    break

            # Deploying replies
            while True:
                await page.wait_for_timeout(1000)

                try:
                    comments.extend(await expect_comments(view_more_replies))
                except TimeoutError:
                    break

            return FacebookComment.sort(comments)

    def scrape_comments(self, url: str) -> List[FacebookComment]:
        if not has_facebook_comments(url):
            raise FacebookInvalidTargetError

        return self.browser.run_in_default_context(self.__scrape_comments, url)
