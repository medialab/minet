# =============================================================================
# Minet Facebook Post Flags CLI Action
# =============================================================================
#
# Logic of the `fb post-flags` action.
#
import casanova
from ural.facebook import is_facebook_post_url

from minet.cli.utils import die, LoadingBar
from minet.facebook.constants import FACEBOOK_WEB_DEFAULT_THROTTLE
from minet.facebook.utils import grab_facebook_cookie
from minet.utils import sleep_with_entropy
from minet.web import request

OTHER_AVAILABILITY_DISCLAIMER = b"This content isn't available at the moment"
CURRENT_AVAILABILITY_DISCLAIMER = b'The link you followed may have expired, or the page may only be visible to an audience'
AVAILABILITY_DISCLAIMER = b'The link you followed may be broken, or the page may have been removed'
LOGIN_DISCLAIMER = b'You must log in to continue'
CAPTCHA = b'id="captcha"'

REPORT_HEADERS = [
    'information_flag_present',
    'fact_check_flag_present',
]
ERROR_PADDING = [''] * (len(REPORT_HEADERS) - 1)


def format_err(err):
    return [err] + ERROR_PADDING


def fetch_facebook_flag(url, cookie):

    headers = {
        'Cookie': cookie,
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    err, response = request(url, headers=headers)

    if err:
        return 'http-error', None

    if response.status == 404:
        return 'not-found', None

    if response.status >= 400:
        return 'http-error', None

    html = response.data

    if CAPTCHA in html:
        die([
            'Rate limit reached!',
            'Last url: %s' % url
        ])

    if (
        CURRENT_AVAILABILITY_DISCLAIMER in html or
        AVAILABILITY_DISCLAIMER in html or
        OTHER_AVAILABILITY_DISCLAIMER in html
    ):
        return 'unavailable', None

    if LOGIN_DISCLAIMER in html:
        return 'you-must-log-in-on-facebook', None

    data = [
        b'Get Vaccine Info' in html,
        b'Checked by independent fact-checkers' in html,
    ]

    return None, data


def facebook_post_flags_action(cli_args):

    cookie = grab_facebook_cookie(cli_args.cookie)

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=REPORT_HEADERS,
        keep=cli_args.select
    )

    # Loading bar
    loading_bar = LoadingBar(
        desc='Fetching post flags',
        unit='post',
        total=cli_args.total
    )

    for row, post_url in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.update()

        if (
            not post_url or
            not is_facebook_post_url(post_url)
        ):
            enricher.writerow(row, format_err('not-facebook-post'))
            continue

        err, data = fetch_facebook_flag(post_url, cookie)

        if err:
            enricher.writerow(row, format_err(err))
        else:
            enricher.writerow(row, data)

        # Throttling
        sleep_with_entropy(FACEBOOK_WEB_DEFAULT_THROTTLE, 5.0)
