# =============================================================================
# Minet Facebook Utils
# =============================================================================
#
# Miscellaneous helpers used by the minet.facebook namespace.
#
from http.cookies import SimpleCookie

from minet.utils import grab_cookies
from minet.facebook.constants import FACEBOOK_URL


def fix_cookie(cookie_string):
    cookie = SimpleCookie()
    cookie.load(cookie_string)

    # NOTE: those cookie items can rat you out
    try:
        del cookie['m_pixel_ratio']
        del cookie['wd']
    except KeyError:
        pass

    cookie['locale'] = 'en_US'

    return '; '.join(key + '=' + morsel.coded_value for key, morsel in cookie.items())


def grab_facebook_cookie(source):
    if source == 'firefox' or source == 'chrome':
        get_cookie_for_url = grab_cookies(source)

        if get_cookie_for_url is None:
            return None

        cookie = get_cookie_for_url(FACEBOOK_URL + '/')

    else:
        cookie = source.strip()

    if not cookie:
        return None

    return fix_cookie(cookie)
