# =============================================================================
# Minet Facebook Utils
# =============================================================================
#
# Miscellaneous helpers used by the minet.facebook namespace.
#
from typing import Callable, Awaitable

import asyncio
from http.cookies import SimpleCookie
from playwright.async_api import Page, Response

from minet.cookies import coerce_cookie_for_url_from_browser
from minet.facebook.constants import FACEBOOK_URL


def fix_cookie(cookie_string):
    cookie = SimpleCookie()
    cookie.load(cookie_string)

    # NOTE: those cookie items can rat you out
    cookie.pop("m_pixel_ratio", None)
    cookie.pop("wd", None)
    cookie.pop("fr", None)

    # NOTE: cookie mangling of the `locale` does not work anymore
    # cookie["locale"] = "en_US"

    return "; ".join(key + "=" + morsel.coded_value for key, morsel in cookie.items())


def grab_facebook_cookie(source):
    cookie = coerce_cookie_for_url_from_browser(source, FACEBOOK_URL + "/")

    if not cookie or "c_user=" not in cookie.lower():
        return None

    return fix_cookie(cookie)


async def try_expect_response(
    page: Page,
    action: Callable[[Page], Awaitable[None]],
    response_predicate: Callable[[Response], bool],
) -> Response:
    selected_response = None
    event = asyncio.Event()

    def release() -> None:
        page.remove_listener("response", listener)
        event.set()

    def listener(response: Response) -> None:
        nonlocal selected_response

        if not response_predicate(response):
            return

        selected_response = response

        release()

    async def guarded_action() -> None:
        try:
            await action(page)
        except Exception:
            release()
            raise

    page.on("response", listener)

    await asyncio.gather(guarded_action(), event.wait())

    assert selected_response is not None

    return selected_response
