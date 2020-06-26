# =============================================================================
# Minet Facebook CLI Action Utils
# =============================================================================
#
# Miscellaneous helpers used by `minet fb`.
#
from http.cookies import SimpleCookie

from minet.utils import grab_cookies
from minet.cli.utils import die
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


def grab_facebook_cookie(namespace):
    if namespace.cookie == 'firefox' or namespace.cookie == 'chrome':
        get_cookie_for_url = grab_cookies(namespace.cookie)

        if get_cookie_for_url is None:
            die('Could not extract cookies from %s.' % namespace.cookie)

        cookie = get_cookie_for_url(FACEBOOK_URL)

    else:
        cookie = namespace.cookie.strip()

    if not cookie:
        die([
            'Relevant cookie not found.',
            'A Facebook authentication cookie is necessary to be able to access Facebook pages.',
            'Use the --cookie flag to choose a browser from which to extract the cookie or give your cookie directly.'
        ])

    return fix_cookie(cookie)
