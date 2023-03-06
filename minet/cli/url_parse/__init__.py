from argparse import Action

from minet.cli.argparse import command, BooleanAction


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
    "minet.cli.url_parse.url_parse",
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
    variadic_input={"dummy_column": "url", "item_label": "url"},
    arguments=[
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
