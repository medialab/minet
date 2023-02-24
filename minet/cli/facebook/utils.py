from minet.constants import COOKIE_BROWSERS
from minet.cli.utils import with_fatal_errors

from minet.facebook.exceptions import FacebookInvalidCookieError


def fatal_errors_hook(_, e):
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


def print_translation_warning_if_needed(loading_bar, translated_langs, post):
    if post.translated_text and post.translated_from not in translated_langs:
        translated_langs.add(post.translated_from)
        lines = [
            "[warning]Found text translated from %s![/warning]" % post.translated_from,
            "Since it means original text may not be entirely retrieved you might want",
            'to edit your Facebook language settings to add "%s" to'
            % post.translated_from,
            'the "Languages you don\'t want to be offered translations for" list here:',
            "https://www.facebook.com/settings/?tab=language",
            "",
        ]

        loading_bar.print(lines)
