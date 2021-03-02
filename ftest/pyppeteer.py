import asyncio
from pyppeteer import launch, connect
from quenouille import imap_unordered
from functools import partial

URLS = [
    'https://www.lemonde.fr/',
    'https://www.lefigaro.fr/',
    'https://www.liberation.fr/'
]

async def boot():
    browser = await launch(
        handleSIGINT=False,
        handleSIGTERM=False,
        handleSIGHUP=False
    )

    endpoint = browser.wsEndpoint

    return endpoint

LOOP = asyncio.get_event_loop()
ENDPOINT = LOOP.run_until_complete(boot())

async def work(url):
    # browser = await launch(
    #     handleSIGINT=False,
    #     handleSIGTERM=False,
    #     handleSIGHUP=False
    # )
    browser = await connect(browserWSEndpoint=ENDPOINT)
    page = await browser.newPage()
    await page.goto(url)

    title = await page.evaluate('''
        () => {
            return document.title;
        }
    ''')

    await browser.disconnect()

    return title

def threaded_work(url):
    return asyncio.new_event_loop().run_until_complete(work(url))

def dummy_work(url):
    return url

for title in imap_unordered(URLS, threaded_work, 3):
    print(title)
