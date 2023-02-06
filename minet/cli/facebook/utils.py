from minet.constants import COOKIE_BROWSERS
from minet.cli.utils import with_fatal_errors

from minet.facebook.exceptions import FacebookInvalidCookieError


def fatal_errors_hook(e):
    if isinstance(e, FacebookInvalidCookieError):
        if e.target in COOKIE_BROWSERS:
            return 'Could not extract relevant cookie from "%s".' % e.target

        return [
            "Relevant cookie not found.",
            "A Facebook authentication cookie is necessary to be able to scrape Facebook comments.",
            "Use the --cookie flag to choose a browser from which to extract the cookie or give your cookie directly.",
        ]


def with_facebook_fatal_errors(fn):
    return with_fatal_errors(fatal_errors_hook)(fn)
