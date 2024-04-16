from minet.browser import ThreadsafeBrowser

with ThreadsafeBrowser(headless=True, adblock=True) as browser:
    response = browser.request("https://lemonde.fr", raise_on_statuses=(404,))

    print(response)
    print(response.stack)
    print(response.headers)
