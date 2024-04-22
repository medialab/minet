from playwright.async_api import Page
from minet.browser import ThreadsafeBrowser


with ThreadsafeBrowser(headless=True, adblock=True) as browser:
    response = browser.request("http://lemonde.fr")

    print(response)
    print(response.stack)
    print(response.headers)
    # print(response.body)
