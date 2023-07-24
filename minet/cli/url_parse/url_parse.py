# =============================================================================
# Minet Url Parse CLI Action
# =============================================================================
#
# Logic of the `url-parse` action.
#
from ural import (
    is_url,
    is_shortened_url,
    normalize_url,
    canonicalize_url,
    fingerprint_url,
    get_hostname,
    get_domain_name,
    get_normalized_hostname,
    get_fingerprinted_hostname,
    infer_redirection,
    is_typo_url,
    is_homepage,
    should_resolve,
    could_be_html,
    could_be_rss,
)
from ural.facebook import (
    parse_facebook_url,
    FacebookPost,
    FacebookUser,
    FacebookGroup,
    FacebookHandle,
    FacebookPhoto,
    FacebookVideo,
)
from ural.youtube import (
    parse_youtube_url,
    normalize_youtube_url,
    YoutubeVideo,
    YoutubeUser,
    YoutubeChannel,
)
from ural.twitter import parse_twitter_url, TwitterTweet, TwitterUser

from minet.cli.utils import with_enricher_and_loading_bar

REPORT_HEADERS = [
    "canonicalized_url",
    "normalized_url",
    "fingerprinted_url",
    "inferred_redirection",
    "domain_name",
    "hostname",
    "normalized_hostname",
    "fingerprinted_hostname",
    "probably_shortened",
    "probably_typo",
    "probably_homepage",
    "should_resolve",
    "could_be_html",
    "could_be_rss",
]

FACEBOOK_REPORT_HEADERS = [
    "facebook_type",
    "facebook_id",
    "facebook_full_id",
    "facebook_handle",
    "facebook_normalized_url",
]

YOUTUBE_REPORT_HEADERS = [
    "youtube_type",
    "youtube_id",
    "youtube_name",
    "youtube_normalize_url",
]

TWITTER_REPORT_HEADERS = ["twitter_type", "twitter_user_screen_name", "tweet_id"]


def extract_standard_addendum(cli_args, url):
    return [
        canonicalize_url(url, quoted=cli_args.quoted),
        normalize_url(
            url,
            infer_redirection=cli_args.infer_redirection,
            fix_common_mistakes=cli_args.fix_common_mistakes,
            normalize_amp=cli_args.normalize_amp,
            quoted=cli_args.quoted,
            sort_query=cli_args.sort_query,
            strip_authentication=cli_args.strip_authentication,
            strip_fragment=cli_args.strip_fragment,
            strip_index=cli_args.strip_index,
            strip_irrelevant_subdomains=cli_args.strip_irrelevant_subdomains,
            strip_protocol=cli_args.strip_protocol,
            strip_trailing_slash=cli_args.strip_trailing_slash,
            platform_aware=cli_args.platform_aware,
        ),
        fingerprint_url(
            url,
            strip_suffix=cli_args.strip_suffix,
            platform_aware=cli_args.platform_aware,
        ),
        infer_redirection(url),
        get_domain_name(url),
        get_hostname(url),
        get_normalized_hostname(
            url,
            infer_redirection=cli_args.infer_redirection,
            normalize_amp=cli_args.normalize_amp,
        ),
        get_fingerprinted_hostname(url, strip_suffix=cli_args.strip_suffix),
        "yes" if is_shortened_url(url) else "no",
        "yes" if is_typo_url(url) else "no",
        "yes" if is_homepage(url) else "no",
        "yes" if should_resolve(url) else "no",
        "yes" if could_be_html(url) else "no",
        "yes" if could_be_rss(url) else "no",
    ]


YOUTUBE_TYPES = {
    YoutubeVideo: "video",
    YoutubeUser: "user",
    YoutubeChannel: "channel",
}


def extract_youtube_addendum(url):
    parsed = parse_youtube_url(url)

    if parsed is None:
        return None

    return [
        YOUTUBE_TYPES.get(type(parsed)),
        parsed.id,
        getattr(parsed, "name", ""),
        normalize_youtube_url(url),
    ]


def extract_facebook_addendum(url):
    parsed = parse_facebook_url(url)

    if parsed is None:
        return None

    if isinstance(parsed, FacebookPost):
        return ["post", parsed.id, parsed.full_id or "", "", parsed.url]

    elif isinstance(parsed, FacebookHandle):
        return ["handle", "", "", parsed.handle, parsed.url]

    elif isinstance(parsed, FacebookUser):
        return ["user", parsed.id or "", "", parsed.handle or "", parsed.url]

    elif isinstance(parsed, FacebookGroup):
        return ["group", parsed.id or "", "", parsed.handle or "", parsed.url]

    elif isinstance(parsed, FacebookPhoto):
        return ["photo", parsed.id, "", "", parsed.url]

    elif isinstance(parsed, FacebookVideo):
        return ["video", parsed.id, "", "", parsed.url]

    else:
        raise TypeError("unknown facebook parse result type!")


def extract_twitter_addendum(url):
    parsed = parse_twitter_url(url)

    if parsed is None:
        return None

    if isinstance(parsed, TwitterUser):
        return ["user", parsed.screen_name, ""]

    elif isinstance(parsed, TwitterTweet):
        return ["tweet", parsed.user_screen_name, parsed.id]

    else:
        raise TypeError("unknown twitter parse result type!")


def get_headers(cli_args):
    if cli_args.facebook:
        return FACEBOOK_REPORT_HEADERS
    elif cli_args.youtube:
        return YOUTUBE_REPORT_HEADERS
    elif cli_args.twitter:
        return TWITTER_REPORT_HEADERS

    return REPORT_HEADERS


@with_enricher_and_loading_bar(headers=get_headers, title="Parsing", unit="urls")
def action(cli_args, enricher, loading_bar):
    for row, url in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step():
            url = url.strip()

            if not is_url(url, allow_spaces_in_path=True, require_protocol=False):
                enricher.writerow(row)
                continue

            if cli_args.facebook:
                addendum = extract_facebook_addendum(url)
            elif cli_args.youtube:
                addendum = extract_youtube_addendum(url)
            elif cli_args.twitter:
                addendum = extract_twitter_addendum(url)
            else:
                addendum = extract_standard_addendum(cli_args, url)

            if addendum is None:
                enricher.writerow(row)
                continue

            enricher.writerow(row, addendum)
