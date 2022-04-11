# =============================================================================
# Minet Cookies CLI Action
# =============================================================================
#
# Logic of the cookies action.
#
import csv
import time
import browser_cookie3
from http.cookies import SimpleCookie

from minet.web import CookieResolver
from minet.cli.utils import die


# Taken from: https://github.com/python/cpython/blob/3.9/Lib/http/cookiejar.py
def write_jar_as_text_mozilla(jar, f, ignore_discard=False, ignore_expires=False):
    now = time.time()
    for cookie in jar:
        if not ignore_discard and cookie.discard:
            continue
        if not ignore_expires and cookie.is_expired(now):
            continue
        if cookie.secure:
            secure = "TRUE"
        else:
            secure = "FALSE"
        if cookie.domain.startswith("."):
            initial_dot = "TRUE"
        else:
            initial_dot = "FALSE"
        if cookie.expires is not None:
            expires = str(cookie.expires)
        else:
            expires = ""
        if cookie.value is None:
            # cookies.txt regards 'Set-Cookie: foo' as a cookie
            # with no name, whereas http.cookiejar regards it as a
            # cookie with no value.
            name = ""
            value = cookie.name
        else:
            name = cookie.name
            value = cookie.value
        f.write(
            "\t".join(
                [cookie.domain, initial_dot, cookie.path, secure, expires, name, value]
            )
            + "\n"
        )


COOKIE_CSV_HEADER = [
    "domain",
    "name",
    "value",
    "path",
    "secure",
    "expires",
    "is_expired",
]

MORSEL_CSV_HEADER = ["key", "value"]


def format_cookie_for_csv(cookie):
    return [
        cookie.domain,
        cookie.name,
        cookie.value,
        cookie.path,
        "true" if cookie.secure else "false",
        cookie.expires,
        "true" if cookie.is_expired else "false",
    ]


def format_morsel_for_csv(morsel):
    return [morsel.key, morsel.value]


def cookies_action(cli_args):
    if cli_args.csv:
        output_writer = csv.writer(cli_args.output)

    try:
        jar = getattr(browser_cookie3, cli_args.browser)()
    except browser_cookie3.BrowserCookieError:
        die("Could not extract cookies from %s!" % cli_args.browser)

    if cli_args.url is not None:
        resolver = CookieResolver(jar)

        cookie = resolver(cli_args.url)

        if cookie is not None:

            if cli_args.csv:
                output_writer.writerow(MORSEL_CSV_HEADER)

                parsed = SimpleCookie(cookie)

                for morsel in parsed.values():
                    output_writer.writerow(format_morsel_for_csv(morsel))
            else:
                print(cookie, file=cli_args.output)
        else:
            die(
                "Could not find relevant cookie for %s in %s!"
                % (cli_args.url, cli_args.browser)
            )
    else:
        if cli_args.csv:
            output_writer.writerow(COOKIE_CSV_HEADER)

            for cookie in jar:
                output_writer.writerow(format_cookie_for_csv(cookie))
        else:
            write_jar_as_text_mozilla(jar, cli_args.output)
