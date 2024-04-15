from minet.browser import ThreadsafeBrowser

with ThreadsafeBrowser(headless=False, adblock=True) as browser:
    response = browser.request("https://github.com/emsojemgrjgr")

    print(response)
    print(response.stack)
    print(response.headers)
