from quenouille import imap_unordered
from minet.browser import ThreadsafeBrowser
from playwright.async_api import Page

# ref: https://github.com/microsoft/playwright-python/issues/342
# ref: https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/registry/index.ts

URLS = [
    "https://www.lemonde.fr/",
    "https://lefigaro.fr",
    "https://liberation.fr",
    "https://mediapart.fr",
]


async def get_title(page: Page) -> str:
    return await page.title()


with ThreadsafeBrowser() as browser:

    def worker(url):
        return browser.with_new_page(url, get_title)

    for title in imap_unordered(URLS, worker, 3):
        print(title)
