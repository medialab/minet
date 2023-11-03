from typing import List

import re
import json
from asyncio import gather
from playwright.async_api import BrowserContext, Response, TimeoutError, Locator
from playwright_stealth import stealth_async
from ural.facebook import has_facebook_comments

from minet.browser import ThreadsafeBrowser
from minet.browser.utils import try_expect_response

from minet.facebook.exceptions import FacebookInvalidTargetError
from minet.facebook.types import FacebookComment


VIEW_MORE_COMMENTS_RE = re.compile(r"View\s+.*more\s+comments?", re.I)
VIEW_MORE_REPLIES_RE = re.compile(r"View\s+.*more\s+replies", re.I)
VIEW_MORE_SUBREPLIES_RE = re.compile(r"^\s*\d+\s+replies", re.I)


def is_graphql_comments_response(response: Response) -> bool:
    if "/api/graphql/" not in response.url:
        return False

    friendly_name = response.request.headers.get("x-fb-friendly-name")

    return (
        friendly_name == "CometUFICommentsProviderForDisplayCommentsQuery"
        or friendly_name == "CometUFIFullThreadedSubRepliesListDataProviderQuery"
    )


async def try_to_click(locator: Locator, timeout: int = 500) -> None:
    try:
        await locator.click(timeout=timeout)
    except TimeoutError:
        pass


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

            # NOTE: this removes the overlay prompting you to login. This is
            # useful for debug, but not only because we need to be able to
            # click & scroll the page and the overlay prevents us from doing so.
            async def destroy_overlay():
                try:
                    await page.get_by_text(
                        "Log in or sign up for Facebook to connect with friends, family and people you know."
                    ).wait_for(timeout=3000)
                    await page.evaluate(
                        """
                        () => {
                            const overlay = document.querySelector('[data-nosnippet]');

                            if (!overlay) return;

                            overlay.remove();
                        }
                        """
                    )
                except TimeoutError:
                    pass

            await gather(
                try_to_click(
                    page.get_by_label("Decline optional cookies").first, timeout=3000
                ),
                try_to_click(page.get_by_label("Close").first, timeout=3000),
                destroy_overlay(),
            )

            async def expect_comments(action) -> List[FacebookComment]:
                response = await try_expect_response(
                    page, action, is_graphql_comments_response
                )

                # NOTE: sometimes FB will pack multiple payload in a single
                # ndjson-like body
                text = await response.text()
                first_doc = text.splitlines()[0]
                payload = json.loads(first_doc)

                # with open("./dump.json", "w") as f:
                #     json.dump(payload, f, ensure_ascii=False, indent=2)

                return FacebookComment.from_payload(payload)

            async def select_all_comments():
                await page.get_by_text("Most relevant").first.click()
                await page.get_by_text("All comments").first.click()

            async def view_more_comments():
                await page.get_by_text(VIEW_MORE_COMMENTS_RE).first.click(timeout=3000)

            async def view_more_replies():
                await page.get_by_text(VIEW_MORE_REPLIES_RE).first.click(timeout=3000)

            async def view_more_subreplies():
                await page.get_by_text(VIEW_MORE_SUBREPLIES_RE).first.click(
                    timeout=3000
                )

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

            # Deploying subreplies
            while True:
                await page.wait_for_timeout(1000)

                try:
                    comments.extend(await expect_comments(view_more_subreplies))
                except TimeoutError:
                    break

            # await page.wait_for_timeout(1000000)

            return FacebookComment.sort(comments)

    def scrape_comments(self, url: str) -> List[FacebookComment]:
        if not has_facebook_comments(url):
            raise FacebookInvalidTargetError

        return self.browser.run_in_default_context(self.__scrape_comments, url)
