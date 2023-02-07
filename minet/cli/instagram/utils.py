from minet.constants import COOKIE_BROWSERS
from minet.instagram.exceptions import InstagramInvalidCookieError

from minet.cli.utils import with_fatal_errors


def fatal_errors_hook(cli_args, e):
    if isinstance(e, InstagramInvalidCookieError):
        if cli_args.cookie in COOKIE_BROWSERS:
            return 'Could not extract relevant cookie from "%s".' % cli_args.cookie

        return [
            "Relevant cookie not found.",
            "An Instagram authentication cookie is necessary to be able to scrape Facebook comments.",
            "Use the --cookie flag to choose a browser from which to extract the cookie or give your cookie directly.",
        ]


def with_instagram_fatal_errors(fn):
    return with_fatal_errors(fatal_errors_hook)(fn)
