import asyncio
import threading
from pyppeteer import launch, connect
from quenouille import imap_unordered
from functools import partial

# TODO: add async delete to drop connexion
# TODO: try to give loop to connexion? asyncio.ensure_future
CONNECTION_POOL = []

class ThreadContext(object):
    def __init__(self, endpoint):
        self.loop = asyncio.new_event_loop()
        self.endpoint = endpoint
        self.browser = None

    def run_until_complete(self, task):
        return self.loop.run_until_complete(task)

    def connect(self):
        async def fn():
            self.browser = await connect(browserWSEndpoint=self.endpoint, loop=self.loop)
            CONNECTION_POOL.append(self.browser)

        self.run_until_complete(fn())

local_data = threading.local()

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

    return browser, endpoint

LOOP = asyncio.get_event_loop()
MASTER, ENDPOINT = LOOP.run_until_complete(boot())

async def work(url):
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


async def work_with_connection(browser, url):
    page = await browser.newPage()
    await page.goto(url)

    title = await page.evaluate('''
        () => {
            return document.title;
        }
    ''')

    await page.close()

    return title


def threaded_work(url):
    if not hasattr(local_data, 'context'):
        context = ThreadContext(ENDPOINT)
        context.connect()
        local_data.context = context

    context = local_data.context

    return context.run_until_complete(work(url))

def dummy_work(url):
    return url

for title in imap_unordered(URLS, threaded_work, 3):
    print(title)

# async def cleanup():
#     for browser in CONNECTION_POOL:
#         await browser.disconnect()

# LOOP.run_until_complete(cleanup())


# TODO: thread local + page closing + browser closing
