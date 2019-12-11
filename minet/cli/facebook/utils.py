# =============================================================================
# Minet Facebook CLI Action Utils
# =============================================================================
#
# Miscellaneous helpers used by `minet fb`.
#
from minet.utils import grab_cookies
from minet.cli.utils import die

FACEBOOK_URL = 'https://www.facebook.com/'


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

    return cookie
