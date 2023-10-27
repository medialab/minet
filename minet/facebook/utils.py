# =============================================================================
# Minet Facebook Utils
# =============================================================================
#
# Miscellaneous helpers used by the minet.facebook namespace.
#
from http.cookies import SimpleCookie

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
