import json
from playwright.async_api import BrowserContext, Response

from minet.browser import ThreadsafeBrowser


def is_graphql_comments_response(response: "Response") -> bool:
    if "/api/graphql/" not in response.url:
        return False

    return (
        response.request.headers.get("x-fb-friendly-name")
        == "CometUFICommentsProviderForDisplayCommentsQuery"
    )


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

            async with page.expect_response(
                is_graphql_comments_response
            ) as response_catcher:
                await page.get_by_text("Most relevant").first.click()
                await page.get_by_text("All comments").first.click()

            response = await response_catcher.value
            data = await response.json()

            with open("./dump.json", "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def scrape_comments(self, url: str):
        self.browser.run_in_default_context(self.__scrape_comments, url)
