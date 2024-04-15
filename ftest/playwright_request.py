from minet.browser import ThreadsafeBrowser

with ThreadsafeBrowser(headless=False) as browser:
    response = browser.request("http://lemonde.fr")

    print(response)
