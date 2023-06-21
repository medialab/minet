import asyncio
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from playwright.async_api import async_playwright

# ref: https://github.com/microsoft/playwright-python/issues/342


async def main():
    driver = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()

    async with async_playwright() as playwright:
        print("before launch", playwright.chromium.executable_path)
        browser = await playwright.chromium.launch(headless=True, timeout=5000)
        print("after launch")
        page = await browser.new_page()
        await page.goto("https://echojs.com")
        print(await page.title())
        await browser.close()


asyncio.run(main())
