# =============================================================================
# Minet Url Parse CLI Action
# =============================================================================
#
# Logic of the `url-parse` action.
#
from argparse import Action

from minet.cli.commands import command
from minet.cli.argparse import BooleanAction


class UrlFragmentAction(Action):
    """
    Custom argparse action to handle --dont-* flags and *except-routing flag.
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, cli_args, values, option_string=None):
        attr = (
            False
            if option_string.startswith("--no-") or option_string.startswith("--dont-")
            else True
        )

        if attr and option_string.endswith("except-routing"):
            attr = "except-routing"

        setattr(cli_args, self.dest, attr)


URL_PARSE_COMMAND = command(
    "url-parse",
    "minet.cli.url_parse",
    title="Minet Url Parse Command",
    description="""
        Parse the urls contained in a CSV file using the python `ural`
        library to extract useful information about them such as their
        normalized version, domain name, etc.
    """,
    epilog="""
        columns being added to the output:

        . "normalized_url": urls aggressively normalized by removing any part
          that is not useful to determine which resource it is actually
          pointing at.
        . "inferred_redirection": redirection directly inferred from the
          url without needing to make any HTTP request.
        . "domain_name": TLD-aware domain name of the url.
        . "hostname": full hostname of the url.
        . "normalized_hostname": normalized hostname, i.e. stripped of "www",
          "m" or some language subdomains etc., of the url.
        . "shortened": whether the url is probably shortened or
          not (bit.ly, t.co etc.).
        . "typo": whether the url probably contains typo or not
          (such as inclusive language in french : curieux.se etc.).
        . "homepage": whether the given url looks like a website's
          homepage.
        . "should_resolve": whether the given url looks like something
          we should resolve, i.e. shortened url.

        columns being added with --facebook:

        . "facebook_type": the type of Facebook resource symbolized by the
          parsed url (post, video etc.).
        . "facebook_id": Facebook resource id.
        . "facebook_full_id": Facebook full resource id.
        . "facebook_handle": Facebook handle for people, pages etc.
        . "facebook_normalized_url": normalized Facebook url.

        columns being added with --youtube:

        . "youtube_type": YouTube resource type (video, channel etc.).
        . "youtube_id": YouTube resource id.
        . "youtube_name": YouTube resource name.

        columns being added with --twitter:

        . "twitter_type": Twitter resource type (user or tweet).
        . "twitter_user_screen_name": Twitter user's screen name.
        . "tweet_id": id of tweet.

        examples:

        . Creating a report about a file's urls:
            $ minet url-parse url posts.csv > report.csv

        . Keeping only selected columns from the input file:
            $ minet url-parse url posts.csv -s id,url,title > report.csv

        . Multiple urls joined by separator:
            $ minet url-parse urls posts.csv --separator "|" > report.csv

        . Parsing Facebook urls:
            $ minet url-parse url fbposts.csv --facebook > report.csv

        . Parsing YouTube urls:
            $ minet url-parse url ytvideos.csv --youtube > report.csv

        . Parsing Twitter urls:
            $ minet url-parse url tweets.csv --twitter > report.csv
    """,
    variadic_input=("url", "CSV file containing target urls."),
    selectable=True,
    total=True,
    arguments=[
        {"name": "column", "help": "Name of the column containing urls."},
        {"flag": "--separator", "help": "Split url column by a separator?"},
        {
            "flag": "--facebook",
            "help": "Whether to consider and parse the given urls as coming from Facebook.",
            "action": "store_true",
        },
        {
            "flag": "--twitter",
            "help": "Whether to consider and parse the given urls as coming from Twitter.",
            "action": "store_true",
        },
        {
            "flag": "--youtube",
            "help": "Whether to consider and parse the given urls as coming from YouTube.",
            "action": "store_true",
        },
        {
            "flags": [
                "--infer-redirection",
                "--dont-infer-redirection",
            ],
            "help": "Whether or not to attempt resolving common redirects by leveraging well-known GET parameters when normalizing url. Defaults to infer redirection.",
            "dest": "infer_redirection",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": [
                "--fix-common-mistakes",
                "--dont-fix-common-mistakes",
            ],
            "help": "Whether or not to attempt to fix common URL mistakes when normalizing url. Defaults to fix common mistakes.",
            "dest": "fix_common_mistakes",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": [
                "--normalize-amp",
                "--dont-normalize-amp",
            ],
            "help": "Whether or not to attempt to normalize Google AMP urls when normalizing url. Defaults to normalize amp.",
            "dest": "normalize_amp",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": [
                "--quoted",
                "--no-quoted",
            ],
            "help": "Whether or not to normalize to a quoted or unquoted version of the url when normalizing url. Defaults to quoted.",
            "dest": "quoted",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": [
                "--sort-query",
                "--dont-sort-query",
            ],
            "help": "Whether or not to sort query items when normalizing url. Defaults to sort query.",
            "dest": "sort_query",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": [
                "--strip-authentication",
                "--dont-strip-authentication",
            ],
            "help": "Whether or not to strip authentication when normalizing url. Defaults to strip authentication.",
            "dest": "strip_authentication",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": [
                "--strip-fragment",
                "--dont-strip-fragment",
                "--strip-fragment-except-routing",
            ],
            "help": "Whether or not to strip the url's fragment when normalizing url. If set to `--strip-fragment-except-routing`, will only strip the fragment if the fragment is not deemed to be js routing (i.e. if it contains a `/`). Defaults to strip fragment except routing.",
            "dest": "strip_fragment",
            "action": UrlFragmentAction,
            "default": "except-routing",
        },
        {
            "flags": [
                "--strip-index",
                "--dont-strip-index",
            ],
            "help": "Whether or not to strip trailing index when normalizing url. Defaults to strip index.",
            "dest": "strip_index",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": [
                "--strip-irrelevant-subdomains",
                "--dont-strip-irrelevant-subdomains",
            ],
            "help": "Whether or not to strip trailing irrelevant-subdomains such as `www` etc. when normalizing url. Defaults to no strip irrelevantsubdomains.",
            "dest": "strip_irrelevant_subdomains",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": [
                "--strip-lang-query-items",
                "--dont-strip-lang-query-items",
            ],
            "help": "Whether or not to strip language query items (ex: `gl=pt_BR`) when normalizing url. Defaults to no strip lang query items.",
            "dest": "strip_lang_query_items",
            "action": BooleanAction,
            "default": False,
        },
        {
            "flags": [
                "--strip-lang-subdomains",
                "--dont-strip-lang-subdomains",
            ],
            "help": "Whether or not to strip language subdomains (ex: `fr-FR.lemonde.fr` to only `lemonde.fr` because `fr-FR` isn't a relevant subdomain, it indicates the language and the country) when normalizing url. Defaults to no strip lang subdomains.",
            "dest": "strip_lang_subdomains",
            "action": BooleanAction,
            "default": False,
        },
        {
            "flags": ["--strip-protocol", "--dont-strip-protocol"],
            "help": "Whether or not to strip the protocol when normalizing the url. Defaults to strip protocol.",
            "dest": "strip_protocol",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": [
                "--strip-trailing-slash",
                "--dont-strip-trailing-slash",
            ],
            "help": "Whether or not to trailing slash when normalizing url. Defaults to strip trailing slash.",
            "dest": "strip_trailing_slash",
            "action": BooleanAction,
            "default": True,
        },
    ],
)


REPORT_HEADERS = [
    "normalized_url",
    "inferred_redirection",
    "domain_name",
    "hostname",
    "normalized_hostname",
    "shortened",
    "typo",
    "homepage",
    "should_resolve",
]

FACEBOOK_REPORT_HEADERS = [
    "facebook_type",
    "facebook_id",
    "facebook_full_id",
    "facebook_handle",
    "facebook_normalized_url",
]

YOUTUBE_REPORT_HEADERS = ["youtube_type", "youtube_id", "youtube_name"]

TWITTER_REPORT_HEADERS = ["twitter_type", "twitter_user_screen_name", "tweet_id"]


def action(cli_args):
    import casanova
    from ural import (
        is_url,
        is_shortened_url,
        normalize_url,
        get_hostname,
        get_domain_name,
        get_normalized_hostname,
        infer_redirection,
        is_typo_url,
        is_homepage,
        should_resolve,
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
        YoutubeVideo,
        YoutubeUser,
        YoutubeChannel,
    )
    from ural.twitter import parse_twitter_url, TwitterTweet, TwitterUser

    from minet.cli.utils import LoadingBar

    def extract_standard_addendum(cli_args, url):
        inferred_redirection = infer_redirection(url)

        return [
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
                strip_lang_query_items=cli_args.strip_lang_query_items,
                strip_lang_subdomains=cli_args.strip_lang_subdomains,
                strip_protocol=cli_args.strip_protocol,
                strip_trailing_slash=cli_args.strip_trailing_slash,
            ),
            inferred_redirection if inferred_redirection != url else "",
            get_domain_name(url),
            get_hostname(url),
            get_normalized_hostname(
                url,
                infer_redirection=cli_args.infer_redirection,
                normalize_amp=cli_args.normalize_amp,
                strip_lang_subdomains=cli_args.strip_lang_subdomains,
            ),
            "yes" if is_shortened_url(url) else "",
            "yes" if is_typo_url(url) else "",
            "yes" if is_homepage(url) else "",
            "yes" if should_resolve(url) else "",
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

        return [YOUTUBE_TYPES.get(type(parsed)), parsed.id, getattr(parsed, "name", "")]

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
        multiplex=multiplex,
    )

    loading_bar = LoadingBar(desc="Parsing", unit="row", total=cli_args.total)

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
