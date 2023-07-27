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
        Columns being added to the output:

        . "canonicalized_url": url cleaned up but technically the same.
        . "normalized_url": url aggressively normalized by removing any part
          that is not useful to determine which resource it is actually
          pointing at.
        . "fingerprinted_url": url even more aggressively normalized. Might
          not be valid anymore, but useful for statistical aggregation.
        . "inferred_redirection": redirection directly inferred from the
          url without needing to make any HTTP request.
        . "domain_name": public suffix-aware domain name of the url.
        . "hostname": full hostname of the url.
        . "normalized_hostname": normalized hostname, i.e. stripped of "www",
          "m" or some language subdomains etc., of the url.
        . "fingerprinted_hostname": hostname even more aggressively normalized.
          Might not be valid anymore.
        . "probably_shortened": whether the url is probably shortened or
          not (bit.ly, t.co etc.).
        . "probably_typo": whether the url probably contains typo or not
          (such as inclusive language in french : curieux.se etc.).
        . "probably_homepage": whether the given url looks like a website's
          homepage.
        . "should_resolve": whether the given url looks like something
          we should resolve, i.e. shortened url or DOI etc.
        . "could_be_html": whether the given url could lead to a HTML file.
        . "could_be_rss": whether the given url could lead to a RSS file.

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

        Examples:

        . Creating a report about a file's urls:
            $ minet url-parse url -i posts.csv > report.csv

        . Keeping only selected columns from the input file:
            $ minet url-parse url -i posts.csv -s id,url,title > report.csv

        . Parsing Facebook urls:
            $ minet url-parse url -i fbposts.csv --facebook > report.csv

        . Parsing YouTube urls:
            $ minet url-parse url -i ytvideos.csv --youtube > report.csv

        . Parsing Twitter urls:
            $ minet url-parse url -i tweets.csv --twitter > report.csv
    """,
    variadic_input={"dummy_column": "url", "item_label": "url"},
    arguments=[
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
            "help": "Whether or not to attempt resolving common redirects by leveraging well-known GET parameters when normalizing url.",
            "dest": "infer_redirection",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": [
                "--fix-common-mistakes",
                "--dont-fix-common-mistakes",
            ],
            "help": "Whether or not to attempt to fix common URL mistakes when normalizing url.",
            "dest": "fix_common_mistakes",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": [
                "--normalize-amp",
                "--dont-normalize-amp",
            ],
            "help": "Whether or not to attempt to normalize Google AMP urls when normalizing url.",
            "dest": "normalize_amp",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flag": "--quoted",
            "help": "Whether to produce quoted canonical and normalized version.",
            "action": "store_true",
        },
        {
            "flags": [
                "--sort-query",
                "--dont-sort-query",
            ],
            "help": "Whether or not to sort query items when normalizing url.",
            "dest": "sort_query",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": [
                "--strip-authentication",
                "--dont-strip-authentication",
            ],
            "help": "Whether or not to strip authentication when normalizing url.",
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
            "help": "Whether or not to strip the url's fragment when normalizing url. If set to `--strip-fragment-except-routing`, will only strip the fragment if the fragment is not deemed to be js routing (i.e. if it contains a `/`).",
            "dest": "strip_fragment",
            "action": UrlFragmentAction,
            "default": "except-routing",
        },
        {
            "flags": [
                "--strip-index",
                "--dont-strip-index",
            ],
            "help": "Whether or not to strip trailing index when normalizing url.",
            "dest": "strip_index",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": [
                "--strip-irrelevant-subdomains",
                "--dont-strip-irrelevant-subdomains",
            ],
            "help": "Whether or not to strip trailing irrelevant-subdomains such as `www` etc. when normalizing url.",
            "dest": "strip_irrelevant_subdomains",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": ["--strip-protocol", "--dont-strip-protocol"],
            "help": "Whether or not to strip the protocol when normalizing the url.",
            "dest": "strip_protocol",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flags": [
                "--strip-trailing-slash",
                "--dont-strip-trailing-slash",
            ],
            "help": "Whether or not to trailing slash when normalizing url.",
            "dest": "strip_trailing_slash",
            "action": BooleanAction,
            "default": True,
        },
        {
            "flag": "--strip-suffix",
            "help": "Whether to strip the hostname suffix when fingerprinting the url.",
            "action": "store_true",
        },
        {
            "flag": "--platform-aware",
            "help": "Whether url parsing should know about some specififc platform such as Facebook, YouTube etc. into account when normalizing urls. Note that this is different than activating --facebook or --youtube.",
            "action": "store_true",
        },
    ],
)
