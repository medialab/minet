# =============================================================================
# Minet Facebook Utils
# =============================================================================
#
# Miscellaneous helpers used by the minet.facebook namespace.
#
from http.cookies import SimpleCookie
import re

from minet.web import grab_cookies
from minet.constants import COOKIE_BROWSERS
from minet.facebook.constants import FACEBOOK_URL

NUMBER_RE = re.compile(r"\d+[\.,]?\d*[KM]?")


def fix_cookie(cookie_string):
    cookie = SimpleCookie()
    cookie.load(cookie_string)

    # NOTE: those cookie items can rat you out
    cookie.pop("m_pixel_ratio", None)
    cookie.pop("wd", None)
    cookie.pop("fr", None)
    cookie["locale"] = "en_US"

    return "; ".join(key + "=" + morsel.coded_value for key, morsel in cookie.items())


def grab_facebook_cookie(source):
    if source in COOKIE_BROWSERS:
        get_cookie_for_url = grab_cookies(source)

        if get_cookie_for_url is None:
            return None

        cookie = get_cookie_for_url(FACEBOOK_URL + "/")

    else:
        cookie = source.strip()

    if not cookie or "c_user=" not in cookie.lower():
        return None

    return fix_cookie(cookie)


def clean_likes(text):

    match = NUMBER_RE.search(text)

    if match is None:
        return text

    approx_likes = match.group(0)

    if "K" in approx_likes:
        approx_likes = str(int(float(approx_likes[:-1]) * 10**3))

    elif "M" in approx_likes:
        approx_likes = str(int(float(approx_likes[:-1]) * 10**6))

    approx_likes = approx_likes.replace(",", "")
    approx_likes = approx_likes.replace(".", "")

    return approx_likes
