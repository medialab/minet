from minet.browser import ThreadsafeBrowser

with ThreadsafeBrowser(headless=False, adblock=True) as browser:
    response = browser.request("http://lemonde.fr")

    print(response)
    print(response.stack)
    print(response.headers)
