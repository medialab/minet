# =============================================================================
# Minet Url Parse CLI Action
# =============================================================================
#
# Logic of the `url-parse` action.
#
import casanova
from ural import (
    is_url,
    is_shortened_url,
    normalize_url,
    get_hostname,
    get_domain_name,
    get_normalized_hostname,
    infer_redirection,
    is_typo_url
)
from ural.facebook import (
    parse_facebook_url,
    FacebookPost,
    FacebookUser,
    FacebookGroup,
    FacebookHandle,
    FacebookPhoto,
    FacebookVideo
)
from ural.youtube import (
    parse_youtube_url,
    YoutubeVideo,
    YoutubeUser,
    YoutubeChannel
)
from ural.twitter import (
    parse_twitter_url,
    TwitterTweet,
    TwitterUser
)

from minet.cli.utils import LoadingBar

REPORT_HEADERS = [
    'normalized_url',
    'inferred_redirection',
    'domain_name',
    'hostname',
    'normalized_hostname',
    'probably_shortened',
    'probably_typo'
]

FACEBOOK_REPORT_HEADERS = [
    'facebook_type',
    'facebook_id',
    'facebook_full_id',
    'facebook_handle',
    'facebook_normalized_url'
]

YOUTUBE_REPORT_HEADERS = [
    'youtube_type',
    'youtube_id',
    'youtube_name'
]

TWITTER_REPORT_HEADERS = [
    'twitter_type',
    'twitter_user_screen_name',
    'tweet_id'
]


def extract_standard_addendum(cli_args, url):
    inferred_redirection = infer_redirection(url)

    return [
        normalize_url(
            url,
            strip_protocol=cli_args.strip_protocol,
            strip_trailing_slash=True
        ),
        inferred_redirection if inferred_redirection != url else '',
        get_domain_name(url),
        get_hostname(url),
        get_normalized_hostname(url),
        'yes' if is_shortened_url(url) else '',
        'yes' if is_typo_url(url) else ''
    ]


YOUTUBE_TYPES = {
    YoutubeVideo: 'video',
    YoutubeUser: 'user',
    YoutubeChannel: 'channel'
}


def extract_youtube_addendum(url):
    parsed = parse_youtube_url(url)

    if parsed is None:
        return None

    return [
        YOUTUBE_TYPES.get(type(parsed)),
        parsed.id,
        getattr(parsed, 'name', '')
    ]


def extract_facebook_addendum(url):
    parsed = parse_facebook_url(url)

    if parsed is None:
        return None

    if isinstance(parsed, FacebookPost):
        return ['post', parsed.id, parsed.full_id or '', '', parsed.url]

    elif isinstance(parsed, FacebookHandle):
        return ['handle', '', '', parsed.handle, parsed.url]

    elif isinstance(parsed, FacebookUser):
        return ['user', parsed.id or '', '', parsed.handle or '', parsed.url]

    elif isinstance(parsed, FacebookGroup):
        return ['group', parsed.id or '', '', parsed.handle or '', parsed.url]

    elif isinstance(parsed, FacebookPhoto):
        return ['photo', parsed.id, '', '', parsed.url]

    elif isinstance(parsed, FacebookVideo):
        return ['video', parsed.id, '', '', parsed.url]

    else:
        raise TypeError('unknown facebook parse result type!')


def extract_twitter_addendum(url):
    parsed = parse_twitter_url(url)

    if parsed is None:
        return None

    if isinstance(parsed, TwitterUser):
        return ['user', parsed.screen_name, '']

    elif isinstance(parsed, TwitterTweet):
        return ['tweet', parsed.user_screen_name, parsed.id]

    else:
        raise TypeError('unknown twitter parse result type!')


def url_parse_action(cli_args):
    headers = REPORT_HEADERS

    if cli_args.facebook:
        headers = FACEBOOK_REPORT_HEADERS
    elif cli_args.youtube:
        headers = YOUTUBE_REPORT_HEADERS
    elif cli_args.twitter:
        headers = TWITTER_REPORT_HEADERS

    multiplex = None

    if cli_args.separator is not None:
        multiplex = (cli_args.column, cli_args.separator)

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=headers,
        keep=cli_args.select,
        multiplex=multiplex
    )

    loading_bar = LoadingBar(
        desc='Parsing',
        unit='row',
        total=cli_args.total
    )

    for row, url in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.update()

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
