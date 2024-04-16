from playwright.async_api import Page
from minet.browser import ThreadsafeBrowser


async def callback(page: Page):
    print("Waiting")
    await page.wait_for_url("https://www.lemonde.fr")
    print("Done waiting")


with ThreadsafeBrowser(headless=True, adblock=True) as browser:
    response = browser.request(
        "https://lemonde.fr", raise_on_statuses=(404,), callback=callback
    )

    print(response)
    print(response.stack)
    print(response.headers)
