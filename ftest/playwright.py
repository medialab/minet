import asyncio
from playwright.async_api import async_playwright
from quenouille import imap_unordered

# ref: https://github.com/microsoft/playwright-python/issues/342
# ref: https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/registry/index.ts

URLS = [
    "https://www.lemonde.fr/",
    "https://lefigaro.fr",
    "https://liberation.fr",
    "https://mediapart.fr",
]


async def main():
    loop = asyncio.get_event_loop()

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True, timeout=5000, args=["--remote-debugging-port=9222"]
        )

        connection = await playwright.chromium.connect_over_cdp("http://localhost:9222")
        page = await connection.new_page()
        await page.goto("https://lemonde.fr")
        print(await page.title())
        await connection.close()
        print(connection)
        raise RuntimeError

        async def get_page_title(url: str) -> str:
            page = await browser.new_page()
            await page.goto(url)

            title = await page.title()

            await page.close()

            return title

        def worker(url: str) -> str:
            future = asyncio.run_coroutine_threadsafe(get_page_title(url), loop)
            return future.result()

        for result in imap_unordered(URLS, worker, 3):
            print(result)

        # for url in URLS:
        #     print(url)
        #     print(await get_page_title(url))

        await browser.close()


asyncio.run(main())
