import asyncio
from pyppeteer import launch
from quenouille import imap_unordered
from functools import partial

URLS = [
    'https://www.lemonde.fr/',
    'https://www.lefigaro.fr/',
    'https://www.liberation.fr/'
]

async def work(url):
    browser = await launch(
        handleSIGINT=False,
        handleSIGTERM=False,
        handleSIGHUP=False
    )
    page = await browser.newPage()
    await page.goto(url)

    title = await page.evaluate('''
        () => {
            return document.title;
        }
    ''')

    await browser.close()

    return title

def threaded_work(url):
    return asyncio.new_event_loop().run_until_complete(work(url))

def dummy_work(url):
    return url

for title in imap_unordered(URLS, threaded_work, 3):
    print(title)
