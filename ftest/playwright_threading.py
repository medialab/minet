from quenouille import imap_unordered
from minet.executors import BrowserThreadPoolExecutor
from minet.browser import ThreadsafeBrowser
from playwright.async_api import Page
from ural import get_normalized_hostname

# ref: https://github.com/microsoft/playwright-python/issues/342
# ref: https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/registry/index.ts

URLS = [
    "https://www.lemonde.fr/",
    "https://lefigaro.fr",
    "https://liberation.fr",
    "https://mediapart.fr",
]


async def get_title(page: Page) -> str:
    # path = get_normalized_hostname(page.url) + ".png"  # type: ignore
    # await page.screenshot(path=path, full_page=True)
    return await page.title()


# with ThreadsafeBrowser() as browser:

#     def worker(url):
#         title = browser.run_with_new_page(get_title, url=url)
#         return title

#     for title in imap_unordered(URLS, worker, 3):
#         print(title)

with BrowserThreadPoolExecutor() as pool:
    for result in pool.run_with_new_page(URLS, get_title):
        print(result)
