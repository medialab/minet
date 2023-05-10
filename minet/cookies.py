from typing import Optional, Dict

import browser_cookie3
from urllib.request import Request
from http.cookiejar import CookieJar
from http.cookies import SimpleCookie

from minet.exceptions import UnknownBrowserError, CookieGrabbingError
from minet.constants import COOKIE_BROWSERS


class CookieResolver(object):
    def __init__(self, jar: CookieJar):
        self.jar = jar

    def __call__(self, url: str) -> Optional[str]:
        req = Request(url)
        self.jar.add_cookie_header(req)

        return req.get_header("Cookie") or None


def get_cookie_jar_from_browser(browser: str = "firefox") -> CookieJar:
    fn = getattr(browser_cookie3, browser, None)

    if fn is None:
        raise UnknownBrowserError(browser)

    try:
        return fn()
    except Exception as reason:
        raise CookieGrabbingError(browser, reason=reason)


def get_cookie_resolver_from_browser(browser: str = "firefox") -> CookieResolver:
    return CookieResolver(get_cookie_jar_from_browser(browser))


def coerce_cookie_for_url_from_browser(target: str, url: str) -> Optional[str]:
    if target in COOKIE_BROWSERS:
        get = get_cookie_resolver_from_browser(target)

        return get(url)

    return target.strip()


def get_cookie_morsel_value(cookie: str, key: str) -> str:
    parsed = SimpleCookie()
    parsed.load(cookie)
    return parsed[key].value


def dict_to_cookie_string(d: Dict[str, str]) -> str:
    return "; ".join("%s=%s" % r for r in d.items())


def cookie_string_to_dict(cookie: str) -> Dict[str, str]:
    parsed = SimpleCookie()
    parsed.load(cookie)

    o = {}

    for morsel in parsed.values():
        o[morsel.key] = morsel.value

    return o
