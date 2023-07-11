import asyncio
import threading
from pyppeteer import launch, connect
from quenouille import imap_unordered
from functools import partial

# TODO: add async delete to drop connection
# TODO: try to give loop to connection? asyncio.ensure_future
CONTEXT_POOL = []


class ThreadContext(object):
    def __init__(self, endpoint):
        self.loop = asyncio.new_event_loop()
        self.endpoint = endpoint

        self.browser = self.run_until_complete(
            connect(browserWSEndpoint=self.endpoint, loop=self.loop)
        )

        CONTEXT_POOL.append(self)

    def run_until_complete(self, task):
        return self.loop.run_until_complete(task)


local_data = threading.local()

URLS = [
    "https://www.lemonde.fr/",
    "https://www.lefigaro.fr/",
    "https://www.liberation.fr/",
]


async def boot():
    browser = await launch(handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)

    endpoint = browser.wsEndpoint

    return browser, endpoint


LOOP = asyncio.get_event_loop()
MASTER, ENDPOINT = LOOP.run_until_complete(boot())


# TODO: use incognito browser context?
async def work(url):
    browser = await connect(browserWSEndpoint=ENDPOINT)
    page = await browser.newPage()
    await page.goto(url)

    title = await page.evaluate(
        """
        () => {
            return document.title;
        }
    """
    )

    await browser.disconnect()

    return title


async def work_with_connection(browser, url):
    page = await browser.newPage()
    await page.goto(url)

    title = await page.evaluate(
        """
        () => {
            return document.title;
        }
    """
    )

    await page.close()

    return title


def threaded_work(url):
    if not hasattr(local_data, "context"):
        context = ThreadContext(ENDPOINT)
        local_data.context = context

    context = local_data.context

    return context.run_until_complete(work(url))


def dummy_work(url):
    return url


for title in imap_unordered(URLS, threaded_work, 3):
    print(title)


def cleanup():
    global local_data
    global CONTEXT_POOL

    print("cleanup")
    for context in CONTEXT_POOL:
        context.run_until_complete(context.browser.disconnect())
        context.loop.close()
        del context

    del local_data
    del CONTEXT_POOL

    LOOP.run_until_complete(MASTER.close())


cleanup()


# TODO: thread local + page closing + browser closing
