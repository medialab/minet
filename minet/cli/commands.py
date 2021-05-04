# =============================================================================
# Minet CLI Commands Definition
# =============================================================================
#
# Defining every minet command.
#
import sys
from argparse import FileType
from casanova import (
    LastCellResumer,
    ThreadSafeResumer,
    BatchResumer
)
from ural import is_url

from minet.constants import (
    DEFAULT_THROTTLE,
    DEFAULT_FETCH_MAX_REDIRECTS,
    DEFAULT_RESOLVE_MAX_REDIRECTS
)
from minet.cli.constants import DEFAULT_CONTENT_FOLDER
from minet.cli.argparse import (
    BooleanAction,
    ConfigAction,
    InputFileAction,
    OutputFileAction,
    SplitterType
)

from minet.constants import COOKIE_BROWSERS

from minet.crowdtangle.constants import (
    CROWDTANGLE_SORT_TYPES,
    CROWDTANGLE_SUMMARY_SORT_TYPES,
    CROWDTANGLE_DEFAULT_RATE_LIMIT,
    CROWDTANGLE_SEARCH_FIELDS
)
from minet.facebook.constants import (
    FACEBOOK_MOBILE_DEFAULT_THROTTLE
)
from minet.youtube.constants import (
    YOUTUBE_API_DEFAULT_SEARCH_ORDER,
    YOUTUBE_API_SEARCH_ORDERS
)

TWITTER_API_COMMON_ARGUMENTS = [
    {
        'flag': '--api-key',
        'help': 'Twitter API key.',
        'rc_key': ['twitter', 'api_key'],
        'action': ConfigAction
    },
    {
        'flag': '--api-secret-key',
        'help': 'Twitter API secret key.',
        'rc_key': ['twitter', 'api_secret_key'],
        'action': ConfigAction
    },
    {
        'flag': '--access-token',
        'help': 'Twitter API access token.',
        'rc_key': ['twitter', 'access_token'],
        'action': ConfigAction
    },
    {
        'flag': '--access-token-secret',
        'help': 'Twitter API access token secret.',
        'rc_key': ['twitter', 'access_token_secret'],
        'action': ConfigAction
    }
]

FETCH_COMMON_ARGUMENTS = [
    {
        'flag': '--domain-parallelism',
        'help': 'Max number of urls per domain to hit at the same time. Defaults to 1',
        'type': int,
        'default': 1
    },
    {
        'flags': ['-g', '--grab-cookies'],
        'help': 'Whether to attempt to grab cookies from your computer\'s browser (supports "firefox", "chrome", "chromium", "opera" and "edge").',
        'choices': COOKIE_BROWSERS
    },
    {
        'flags': ['-H', '--header'],
        'help': 'Custom headers used with every requests.',
        'action': 'append',
        'dest': 'headers'
    },
    {
        'flag': '--insecure',
        'help': 'Whether to allow ssl errors when performing requests or not.',
        'action': 'store_true'
    },
    {
        'flags': ['-o', '--output'],
        'action': OutputFileAction,
        'resumer': ThreadSafeResumer
    },
    {
        'flag': '--resume',
        'help': 'Whether to resume from an aborted report.',
        'action': 'store_true'
    },
    {
        'flags': ['-s', '--select'],
        'help': 'Columns of input CSV file to include in the output (separated by `,`).',
        'type': SplitterType()
    },
    {
        'flags': ['-t', '--threads'],
        'help': 'Number of threads to use. Defaults to 25.',
        'type': int,
        'default': 25
    },
    {
        'flag': '--throttle',
        'help': 'Time to wait - in seconds - between 2 calls to the same domain. Defaults to %s.' % DEFAULT_THROTTLE,
        'type': float,
        'default': DEFAULT_THROTTLE
    },
    {
        'flag': '--timeout',
        'help': 'Maximum time - in seconds - to spend for each request before triggering a timeout. Defaults to ~30s.',
        'type': float
    },
    {
        'flag': '--total',
        'help': 'Total number of lines in CSV file. Necessary if you want to display a finite progress indicator for large input files.',
        'type': int
    },
    {
        'flag': '--url-template',
        'help': 'A template for the urls to fetch. Handy e.g. if you need to build urls from ids etc.'
    },
    {
        'flags': ['-X', '--request'],
        'help': 'The http method to use. Will default to GET.',
        'dest': 'method',
        'default': 'GET'
    }
]

MINET_COMMANDS = {

    # Cookies action subparser
    # --------------------------------------------------------------------------
    'cookies': {
        'package': 'minet.cli.cookies',
        'action': 'cookies_action',
        'title': 'Minet Cookies Command',
        'description': '''
            Grab cookies directly from your browsers to use them easily later
            in python scripts, for instance.
        ''',
        'epilog': '''
            examples:

            . Dumping cookie jar from firefox:
                $ minet cookies firefox > jar.txt

            . Dumping cookies as CSV:
                $ minet cookies firefox --csv > cookies.csv

            . Print cookie for lemonde.fr:
                $ minet cookie firefox --url https://www.lemonde.fr

            . Dump cookie morsels for lemonde.fr as CSV:
                $ minet cookie firefox --url https://www.lemonde.fr --csv > morsels.csv
        ''',
        'arguments': [
            {
                'name': 'browser',
                'help': 'Name of the browser from which to grab cookies.',
                'choices': COOKIE_BROWSERS
            },
            {
                'flag': '--csv',
                'help': 'Whether to format the output as CSV. If --url is set, will output the cookie\'s morsels as CSV.',
                'action': 'store_true'
            },
            {
                'flags': ['-o', '--output'],
                'action': OutputFileAction
            },
            {
                'flag': '--url',
                'help': 'If given, only returns full cookie header value for this url.'
            }
        ]
    },

    # Crawl action subparser
    # --------------------------------------------------------------------------
    'crawl': {
        'package': 'minet.cli.crawl',
        'action': 'crawl_action',
        'title': 'Minet Crawl Command',
        'description': '''
            Use multiple threads to crawl the web using minet crawling and
            scraping DSL.
        ''',
        'epilog': '''
            examples:

            . Running a crawler definition:
                $ minet crawl crawler.yml -d crawl-data
        ''',
        'arguments': [
            {
                'name': 'crawler',
                'help': 'Path to the crawler definition file.'
            },
            {
                'flags': ['-d', '--output-dir'],
                'help': 'Output directory.',
                'default': 'crawl'
            },
            {
                'flag': '--resume',
                'help': 'Whether to resume an interrupted crawl.',
                'action': 'store_true'
            },
            {
                'flag': '--throttle',
                'help': 'Time to wait - in seconds - between 2 calls to the same domain. Defaults to %s.' % DEFAULT_THROTTLE,
                'type': float,
                'default': DEFAULT_THROTTLE
            },
        ]
    },

    # Crowdtangle action subparser
    # --------------------------------------------------------------------------
    'crowdtangle': {
        'package': 'minet.cli.crowdtangle',
        'action': 'crowdtangle_action',
        'aliases': ['ct'],
        'title': 'Minet Crowdtangle Command',
        'description': '''
            Gather data from the CrowdTangle APIs easily and efficiently.
        ''',
        'subparsers': {
            'help': 'Action to perform using the CrowdTangle API.',
            'title': 'actions',
            'dest': 'ct_action',
            'common_arguments': [
                {
                    'flag': '--rate-limit',
                    'help': 'Authorized number of hits by minutes. Defaults to %i. Rcfile key: crowdtangle.rate_limit' % CROWDTANGLE_DEFAULT_RATE_LIMIT,
                    'type': int,
                    'default': CROWDTANGLE_DEFAULT_RATE_LIMIT,
                    'rc_key': ['crowdtangle', 'rate_limit'],
                    'action': ConfigAction
                },
                {
                    'flags': ['-t', '--token'],
                    'help': 'CrowdTangle dashboard API token. Rcfile key: crowdtangle.token',
                    'action': ConfigAction,
                    'rc_key': ['crowdtangle', 'token']
                }
            ],
            'commands': {
                'leaderboard': {
                    'title': 'Minet CrowdTangle Leaderboard Command',
                    'description': '''
                        Gather information and aggregated stats about pages and groups of the designated dashboard (indicated by a given token).

                        For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Leaderboard.
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching accounts statistics for every account in your dashboard:
                            $ minet ct leaderboard --token YOUR_TOKEN > accounts-stats.csv
                    ''',
                    'arguments': [
                        {
                            'flag': '--no-breakdown',
                            'help': 'Whether to skip statistics breakdown by post type in the CSV output.',
                            'dest': 'breakdown',
                            'action': BooleanAction,
                            'default': True
                        },
                        {
                            'flags': ['-f', '--format'],
                            'help': 'Output format. Defaults to `csv`.',
                            'choices': ['csv', 'jsonl'],
                            'default': 'csv'
                        },
                        {
                            'flags': ['-l', '--limit'],
                            'help': 'Maximum number of accounts to retrieve. Will fetch every account by default.',
                            'type': int
                        },
                        {
                            'flag': '--list-id',
                            'help': 'Optional list id from which to retrieve accounts.'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction
                        }
                    ]
                },
                'lists': {
                    'title': 'Minet CrowdTangle Lists Command',
                    'description': '''
                        Retrieve the lists from a CrowdTangle dashboard (indicated by a given token).

                        For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Lists.
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching a dashboard's lists:
                            $ minet ct lists --token YOUR_TOKEN > lists.csv
                    ''',
                    'arguments': [
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction
                        }
                    ]
                },
                'posts': {
                    'title': 'Minet CrowdTangle Posts Command',
                    'description': '''
                        Gather post data from the designated dashboard (indicated by a given token).

                        For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Posts.
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching the 500 most latest posts from a dashboard (a start date must be precised):
                            $ minet ct posts --token YOUR_TOKEN --limit 500 --start-date 2021-01-01 > latest-posts.csv

                        . If your collection is interrupted, it can be restarted from the last data collected with the --resume option:
                            $ minet ct posts --token YOUR_TOKEN --limit 500 --start-date 2021-01-01 --resume --output latest-posts.csv

                        . Fetching all the posts from a specific list of groups or pages:
                            $ minet ct posts --token YOUR_TOKEN --start-date 2021-01-01 --list-ids YOUR_LIST_ID > posts_from_one_list.csv

                        To know the different list ids associated with your dashboard:
                            $ minet ct lists --token YOUR_TOKEN
                    ''',
                    'arguments': [
                        {
                            'flag': '--chunk-size',
                            'help': 'When sorting by date (default), the number of items to retrieve before shifting the inital query to circumvent the APIs limitations. Defaults to 500.',
                            'type': int,
                            'default': 500
                        },
                        {
                            'flag': '--end-date',
                            'help': 'The latest date at which a post could be posted (UTC!). You can pass just a year or a year-month for convenience.'
                        },
                        {
                            'flags': ['-f', '--format'],
                            'help': 'Output format. Defaults to `csv`.',
                            'choices': ['csv', 'jsonl'],
                            'default': 'csv'
                        },
                        {
                            'flag': '--language',
                            'help': 'Language of posts to retrieve.'
                        },
                        {
                            'flags': ['-l', '--limit'],
                            'help': 'Maximum number of posts to retrieve. Will fetch every post by default.',
                            'type': int
                        },
                        {
                            'flag': '--list-ids',
                            'help': 'Ids of the lists from which to retrieve posts, separated by commas.',
                            'type': SplitterType()
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction,
                            'resumer': LastCellResumer,
                            'resumer_kwargs': {
                                'value_column': 'datetime'
                            }
                        },
                        {
                            'flag': '--resume',
                            'help': 'Whether to resume an interrupted collection. Requires -o/--output & --sort-by date',
                            'action': 'store_true'
                        },
                        {
                            'flag': '--sort-by',
                            'help': 'The order in which to retrieve posts. Defaults to `date`.',
                            'choices': CROWDTANGLE_SORT_TYPES,
                            'default': 'date'
                        },
                        {
                            'flag': '--start-date',
                            'help': 'The earliest date at which a post could be posted (UTC!). You can pass just a year or a year-month for convenience.',
                            'required': True
                        }
                    ]
                },
                'posts-by-id': {
                    'title': 'Minet CrowdTangle Post By Id Command',
                    'description': '''
                        Retrieve metadata about batches of posts using Crowdtangle's API.

                        For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Posts#get-postid.
                    ''',
                    'epilog': '''
                        examples:

                        . Retrieving information about a batch of posts:
                            $ minet ct posts-by-id post-url posts.csv --token YOUR_TOKEN > metadata.csv

                        . Retrieving information about a single post:
                            $ minet ct posts-by-id 1784333048289665 --token YOUR_TOKEN
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the posts URL or id in the CSV file.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired URLs or ids.',
                            'type': FileType('r', encoding='utf-8'),
                            'default': sys.stdin,
                            'nargs': '?'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--resume',
                            'help': 'Whether to resume an aborted collection.',
                            'action': 'store_true'
                        },
                        {
                            'flag': '--total',
                            'help': 'Total number of posts. Necessary if you want to display a finite progress indicator.',
                            'type': int
                        }
                    ]
                },
                'search': {
                    'title': 'Minet CrowdTangle Search Command',
                    'description': '''
                        Search posts on the whole CrowdTangle platform.

                        For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Search.
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching all the 2021 posts containing the words 'acetylsalicylic acid':
                            $ minet ct search 'acetylsalicylic acid' --start-date 2021-01-01 --token YOUR_TOKEN > posts.csv
                    ''',
                    'arguments': [
                        {
                            'name': 'terms',
                            'help': 'The search query term or terms.'
                        },
                        {
                            'flag': '--and',
                            'help': 'AND clause to add to the query terms.'
                        },
                        {
                            'flag': '--chunk-size',
                            'help': 'When sorting by date (default), the number of items to retrieve before shifting the inital query to circumvent the APIs limitations. Defaults to 500.',
                            'type': int,
                            'default': 500
                        },
                        {
                            'flag': '--end-date',
                            'help': 'The latest date at which a post could be posted (UTC!). You can pass just a year or a year-month for convenience.'
                        },
                        {
                            'flags': ['-f', '--format'],
                            'help': 'Output format. Defaults to `csv`.',
                            'choices': ['csv', 'jsonl'],
                            'default': 'csv'
                        },
                        {
                            'flag': '--in-list-ids',
                            'help': 'Ids of the lists in which to search, separated by commas.',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--language',
                            'help': 'Language ISO code like "fr" or "zh-CN".'
                        },
                        {
                            'flags': ['-l', '--limit'],
                            'help': 'Maximum number of posts to retrieve. Will fetch every post by default.',
                            'type': int
                        },
                        {
                            'flag': '--not-in-title',
                            'help': 'Whether to search terms in account titles also.',
                            'action': 'store_true'
                        },
                        {
                            'flag': '--offset',
                            'help': 'Count offset.',
                            'type': int
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction
                        },
                        {
                            'flags': ['-p', '--platforms'],
                            'help': 'The platforms from which to retrieve links (facebook, instagram, or reddit). This value can be comma-separated.',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--search-field',
                            'help': 'In what to search the query. Defaults to `text_fields_and_image_text`.',
                            'choices': CROWDTANGLE_SEARCH_FIELDS
                        },
                        {
                            'flag': '--sort-by',
                            'help': 'The order in which to retrieve posts. Defaults to `date`.',
                            'choices': CROWDTANGLE_SORT_TYPES,
                            'default': 'date'
                        },
                        {
                            'flag': '--start-date',
                            'help': 'The earliest date at which a post could be posted (UTC!). You can pass just a year or a year-month for convenience.',
                            'required': True
                        },
                        {
                            'flag': '--types',
                            'help': 'Types of post to include, separated by comma.',
                            'type': SplitterType()
                        }
                    ]
                },
                'summary': {
                    'title': 'Minet CrowdTangle Link Summary Command',
                    'description': '''
                        Retrieve aggregated statistics about link sharing on the Crowdtangle API and by platform.

                        For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Links.
                    ''',
                    'epilog': '''
                        examples:

                        . Computing a summary of aggregated stats for urls contained in a CSV row:
                            $ minet ct summary url urls.csv --token YOUR_TOKEN --start-date 2019-01-01 > summary.csv
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the URL in the CSV file.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired URLs.',
                            'action': InputFileAction,
                            'dummy_csv_column': 'url'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction
                        },
                        {
                            'flags': ['-p', '--platforms'],
                            'help': 'The platforms from which to retrieve links (facebook, instagram, or reddit). This value can be comma-separated.',
                            'type': SplitterType()
                        },
                        {
                            'name': '--posts',
                            'help': 'Path to a file containing the retrieved posts.',
                            'action': OutputFileAction,
                            'stdout_fallback': False
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--sort-by',
                            'help': 'How to sort retrieved posts. Defaults to `date`.',
                            'choices': CROWDTANGLE_SUMMARY_SORT_TYPES,
                            'default': 'date'
                        },
                        {
                            'flag': '--start-date',
                            'help': 'The earliest date at which a post could be posted (UTC!). You can pass just a year or a year-month for convenience.'
                        },
                        {
                            'flag': '--total',
                            'help': 'Total number of HTML documents. Necessary if you want to display a finite progress indicator.',
                            'type': int
                        }
                    ]
                }
            }
        }
    },

    # Extract action subparser
    # -------------------------------------------------------------------------
    'extract': {
        'package': 'minet.cli.extract',
        'action': 'extract_action',
        'title': 'Minet Extract Command',
        'description': '''
            Use multiple processes to extract raw content and various metadata
            from a batch of HTML files. This command can either work on a
            `minet fetch` report or on a bunch of files. It will output an
            augmented report with the extracted text.

            Extraction is performed using the `trafilatura` library by Adrien
            Barbaresi. More information about the library can be found here:
            https://github.com/adbar/trafilatura

            Note that this methodology mainly targets news article and may fail
            to extract relevant content from other kind of web pages.
        ''',
        'epilog': '''

            columns being added to the output:

            . "extract_error": any error that happened when extracting content.
            . "canonical_url": canonical url of target html, extracted from
              link[rel=canonical].
            . "title": title of the web page, from <title> usually.
            . "description": description of the web page, as found in its
              metadata.
            . "raw_content": main content of the web page as extracted.
            . "comments": comment text whenever the heuristics succeeds in
              identifying them.
            . "author": inferred author of the web page article when found in
              its metadata.
            . "categories": list of categories extracted from the web page's
              metadata, separated by "|".
            . "tags": list of tags extracted from the web page's metadata,
              separated by "|".
            . "date": date of publication of the web page article when found in
              its metadata.
            . "sitename": canonical name as declared by the website.

            examples:

            . Extracting text from a `minet fetch` report:
                $ minet extract report.csv > extracted.csv

            . Extracting text from a bunch of files using a glob pattern:
                $ minet extract --glob "./content/**/*.html" > extracted.csv

            . Working on a report from stdin:
                $ minet fetch url_column file.csv | minet extract > extracted.csv
        ''',
        'arguments': [
            {
                'name': 'report',
                'help': 'Input CSV fetch action report file.',
                'action': InputFileAction
            },
            {
                'flags': ['-g', '--glob'],
                'help': 'Whether to extract text from a bunch of html files on disk matched by a glob pattern rather than sourcing them from a CSV report.'
            },
            {
                'flags': ['-i', '--input-dir'],
                'help': 'Directory where the HTML files are stored. Defaults to "%s" if --glob is not set.' % DEFAULT_CONTENT_FOLDER
            },
            {
                'flags': ['-o', '--output'],
                'action': OutputFileAction
            },
            {
                'flags': ['-p', '--processes'],
                'help': 'Number of processes to use. Defaults to roughly half of the available CPUs.',
                'type': int
            },
            {
                'flags': ['-s', '--select'],
                'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                'type': SplitterType()
            },
            {
                'flag': '--total',
                'help': 'Total number of HTML documents. Necessary if you want to display a finite progress indicator.',
                'type': int
            }
        ]
    },

    # Facebook actions subparser
    # -------------------------------------------------------------------------
    'facebook': {
        'package': 'minet.cli.facebook',
        'action': 'facebook_action',
        'aliases': ['fb'],
        'title': 'Minet Facebook Command',
        'description': '''
            Collects data from Facebook.
        ''',
        'subparsers': {
            'help': 'Action to perform to collect data on Facebook',
            'title': 'actions',
            'dest': 'fb_action',
            'commands': {
                'comments': {
                    'title': 'Minet Facebook Comments Command',
                    'description': '''
                        Scrape a Facebook post's comments.

                        This requires to be logged in to a Facebook account, so
                        by default this command will attempt to grab the relevant
                        authentication cookies from a local Firefox browser.

                        If you want to grab cookies from another browser or want
                        to directly pass the cookie as a string, check out the
                        -c/--cookie flag.
                    ''',
                    'epilog': '''
                        examples:

                        . Scraping a post's comments:
                            $ minet fb comments https://www.facebook.com/groups/186982532676569/permalink/4096995827030341/ > comments.csv

                        . Grabbing cookies from chrome:
                            $ minet fb comments -c chrome https://www.facebook.com/groups/186982532676569/permalink/4096995827030341/ > comments.csv

                        . Scraping comments from multiple posts listed in a CSV file:
                            $ minet fb comments post_url posts.csv > comments.csv
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Column of the CSV file containing post urls or a single post url.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the post urls.',
                            'action': InputFileAction,
                            'dummy_csv_column': 'post_url'
                        },
                        {
                            'flags': ['-c', '--cookie'],
                            'help': 'Authenticated cookie to use or browser from which to extract it (supports "firefox", "chrome", "chromium", "opera" and "edge"). Defaults to "firefox".',
                            'default': 'firefox',
                            'rc_key': ['facebook', 'cookie'],
                            'action': ConfigAction
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--throttle',
                            'help': 'Throttling time, in seconds, to wait between each request.',
                            'type': float,
                            'default': FACEBOOK_MOBILE_DEFAULT_THROTTLE
                        }
                    ]
                },
                'posts': {
                    'title': 'Minet Facebook Posts Command',
                    'description': '''
                        Scrape Facebook posts.

                        This requires to be logged in to a Facebook account, so
                        by default this command will attempt to grab the relevant
                        authentication cookies from a local Firefox browser.

                        If you want to grab cookies from another browser or want
                        to directly pass the cookie as a string, check out the
                        -c/--cookie flag.

                        Scraping posts currently only works for Facebook groups.

                        Note that, by default, Facebook will translate post text
                        when they are not written in a language whitelisted here:
                        https://www.facebook.com/settings/?tab=language

                        In this case, minet will output both the original text and
                        the translated one. But be aware that original text may be
                        truncated, so you might want to edit your Facebook settings
                        using the url above to make sure text won't be translated
                        for posts you are interested in.

                        Of course, the CLI will warn you when translated text is
                        found so you can choose to edit your settings early as
                        as possible.

                        Finally, some post text is always truncated on Facebook
                        when displayed in lists. This text is not yet entirely
                        scraped by minet at this time.
                    ''',
                    'epilog': '''
                        examples:

                        . Scraping a group's posts:
                            $ minet fb posts https://www.facebook.com/groups/444175323127747 > posts.csv

                        . Grabbing cookies from chrome:
                            $ minet fb posts -c chrome https://www.facebook.com/groups/444175323127747 > posts.csv

                        . Scraping posts from multiple groups listed in a CSV file:
                            $ minet fb posts group_url groups.csv > posts.csv
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Column of the CSV file containing group urls or a single group url.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the group urls.',
                            'action': InputFileAction,
                            'dummy_csv_column': 'group_url'
                        },
                        {
                            'flags': ['-c', '--cookie'],
                            'help': 'Authenticated cookie to use or browser from which to extract it (supports "firefox", "chrome", "chromium", "opera" and "edge"). Defaults to "firefox".',
                            'default': 'firefox',
                            'rc_key': ['facebook', 'cookie'],
                            'action': ConfigAction
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--throttle',
                            'help': 'Throttling time, in seconds, to wait between each request.',
                            'type': float,
                            'default': FACEBOOK_MOBILE_DEFAULT_THROTTLE
                        }
                    ]
                },
                'post-stats': {
                    'title': 'Minet Facebook Post Stats Command',
                    'description': '''
                        Retrieve statistics about a given list of Facebook posts.
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching stats about lists of posts in a CSV file:
                            $ minet fb post-stats post_url fb-posts.csv
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the CSV column containing the posts\' urls.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the posts.',
                            'action': InputFileAction
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--total',
                            'help': 'Total number of lines in CSV file. Necessary if you want to display a finite progress indicator for large input files.',
                            'type': int
                        }
                    ]
                },
                'url-likes': {
                    'title': 'Minet Facebook Url Likes Command',
                    'description': '''
                        Retrieve the approximate number of "likes" each url of
                        a CSV file has on Facebook.

                        It is found by scraping Facebook's like button, which only give a
                        rough estimation of the real number like so: "1.2K people like this."

                        Note that the number does not actually only correspond to the number of
                        like reactions, but rather to the sum of like, love, ahah, angry, etc.
                        reactions plus the number of comments and shares that the URL generated on Facebook.
                    ''',
                    'epilog': '''
                        example:

                        . Retrieving likes for the urls listed in a CSV file:
                            $ minet fb url-likes url url.csv > url_likes.csv
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the URL in the CSV file or a single url.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired URLs.',
                            'action': InputFileAction,
                            'dummy_csv_column': 'url'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--total',
                            'help': 'Total number of lines in CSV file. Necessary if you want to display a finite progress indicator for large input files.',
                            'type': int
                        }
                    ]
                }
            }
        }
    },

    # Fetch action subparser
    # --------------------------------------------------------------------------
    'fetch': {
        'package': 'minet.cli.fetch',
        'action': 'fetch_action',
        'title': 'Minet Fetch Command',
        'description': '''
            Use multiple threads to fetch batches of urls from a CSV file. The
            command outputs a CSV report with additional metadata about the
            HTTP calls and will generally write the retrieved files in a folder
            given by the user.
        ''',
        'epilog': '''
            columns being added to the output:

            . "index": index of the line in the original file (the output will be
              arbitrarily ordered since multiple requests are performed concurrently).
            . "resolved": final resolved url (after solving redirects) if different
              from requested url.
            . "status": HTTP status code of the request, e.g. 200, 404, 503 etc.
            . "error": an error code if anything went wrong when performing the request.
            . "filename": path to the downloaded file, relative to the folder given
              through -d/--output-dir.
            . "mimetype": detected mimetype of the requested file.
            . "encoding": detected encoding of the requested file if relevant.
            . "raw_contents": if --contents-in-report is set, will contain the
              downloaded text and the file won't be written.

            --folder-strategy options:

            . "flat": default choice, all files will be written in the indicated
              content folder.

            . "prefix-x": e.g. "prefix-4", files will be written in folders
              having a name that is the first x characters of the file's name.
              This is an efficient way to partition content into folders containing
              roughly the same number of files if the file names are random (which
              is the case by default since uuids will be used).

            . "hostname": files will be written in folders based on their url's
              full host name.

            . "normalized-hostname": files will be written in folders based on
              their url's hostname stripped of some undesirable parts (such as
              "www.", or "m." or "fr.", for instance).

            examples:

            . Fetching a batch of url from existing CSV file:
                $ minet fetch url_column file.csv > report.csv

            . CSV input from stdin:
                $ xsv select url_column file.csv | minet fetch url_column > report.csv

            . Fetching a single url, useful to pipe into `minet scrape`:
                $ minet fetch http://google.com | minet scrape ./scrape.json > scraped.csv
        ''',
        'arguments': [
            {
                'name': 'column',
                'help': 'Column of the CSV file containing urls to fetch or a single url to fetch.'
            },
            {
                'name': 'file',
                'help': 'CSV file containing the urls to fetch.',
                'action': InputFileAction,
                'dummy_csv_column': 'url',
                'dummy_csv_guard': is_url,
                'dummy_csv_error': 'single argument is expected to be a valid url!'
            },
            *FETCH_COMMON_ARGUMENTS,
            {
                'flag': '--max-redirects',
                'help': 'Maximum number of redirections to follow before breaking. Defaults to 5.',
                'type': int,
                'default': DEFAULT_FETCH_MAX_REDIRECTS
            },
            {
                'flag': '--compress',
                'help': 'Whether to compress the contents.',
                'action': 'store_true'
            },
            {
                'flags': ['--contents-in-report', '--no-contents-in-report'],
                'help': 'Whether to include retrieved contents, e.g. html, directly in the report\nand avoid writing them in a separate folder. This requires to standardize\nencoding and won\'t work on binary formats.',
                'dest': 'contents_in_report',
                'action': BooleanAction
            },
            {
                'flags': ['-d', '--output-dir'],
                'help': 'Directory where the fetched files will be written. Defaults to "%s".' % DEFAULT_CONTENT_FOLDER,
                'default': DEFAULT_CONTENT_FOLDER
            },
            {
                'flags': ['-f', '--filename'],
                'help': 'Name of the column used to build retrieved file names. Defaults to a md5 hash of final url. If the provided file names have no extension (e.g. ".jpg", ".pdf", etc.) the correct extension will be added depending on the file type.'
            },
            {
                'flag': '--filename-template',
                'help': 'A template for the name of the fetched files.'
            },
            {
                'flag': '--folder-strategy',
                'help': 'Name of the strategy to be used to dispatch the retrieved files into folders to alleviate issues on some filesystems when a folder contains too much files. Note that this will be applied on top of --filename-template. Defaults to "flat". All of the strategies are described at the end of this help.',
                'default': 'flat'
            },
            {
                'flag': '--keep-failed-contents',
                'help': 'Whether to keep & write contents for failed (i.e. non-200) http requests.',
                'action': 'store_true'
            },
            {
                'flag': '--standardize-encoding',
                'help': 'Whether to systematically convert retrieved text to UTF-8.',
                'action': 'store_true'
            }
        ]
    },

    # Google action subparser
    # --------------------------------------------------------------------------
    'google': {
        'package': 'minet.cli.google',
        'action': 'google_action',
        'title': 'Minet Google Command',
        'description': '''
            Commands related to Google and Google Drive.
        ''',
        'subparsers': {
            'help': 'Action to perform.',
            'title': 'actions',
            'dest': 'google_action',
            'commands': {
                'sheets': {
                    'title': 'Minet Google Sheets Command',
                    'description': '''
                        Grab the given google spreadsheet as a CSV file from
                        its url, its sharing url or id.

                        It can access public spreadsheets without issues, but to
                        you will need to tell the command how to retrieve Google
                        drive authentication cookies to also be able to access
                        private ones.

                        Also note that by default, the command will try to access
                        your spreadsheet using your first 4 connected Google
                        accounts.

                        If you have more connected accounts or know beforehand
                        to which account some spreadsheets are tied to, be sure
                        to give --authuser.
                    ''',
                    'epilog': '''
                        examples:

                        . Exporting from the spreadsheet id:
                            $ minet google sheets 1QXQ1yaNYrVUlMt6LQ4jrLGt_PvZI9goozYiBTgaC4RI > file.csv

                        . Using your Firefox authentication cookies:
                            $ minet google sheets --cookie firefox 1QXQ1yaNYrVUlMt6LQ4jrLGt_PvZI9goozYiBTgaC4RI > file.csv
                    ''',
                    'arguments': [
                        {
                            'name': 'url',
                            'help': 'Url, sharing url or id of the spreadsheet to export.'
                        },
                        {
                            'flags': ['-a', '--authuser'],
                            'help': 'Connected google account number to use.',
                            'type': int
                        },
                        {
                            'flags': ['-c', '--cookie'],
                            'help': 'Google Drive cookie or browser from which to extract it (supports "firefox", "chrome", "chromium", "opera" and "edge").'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction
                        }
                    ]
                }
            }
        }
    },

    # Hyphe action subparser
    # -------------------------------------------------------------------------
    'hyphe': {
        'package': 'minet.cli.hyphe',
        'action': 'hyphe_action',
        'title': 'Minet Hyphe Command',
        'description': '''
            Commands related to the Hyphe crawler.
        ''',
        'subparsers': {
            'help': 'Action to perform.',
            'title': 'actions',
            'dest': 'hyphe_action',
            'commands': {
                'dump': {
                    'title': 'Minet Hyphe Dump Command',
                    'description': '''
                        Command dumping page-level information from a given
                        Hyphe corpus.
                    ''',
                    'epilog': '''
                        examples:

                        . Dumping a corpus into the ./corpus directory:
                            $ minet hyphe dump http://myhyphe.com/api/ corpus-name -d corpus
                    ''',
                    'arguments': [
                        {
                            'name': 'url',
                            'help': 'Url of the Hyphe API.'
                        },
                        {
                            'name': 'corpus',
                            'help': 'Id of the corpus.'
                        },
                        {
                            'flags': ['-d', '--output-dir'],
                            'help': 'Output directory for dumped files. Will default to some name based on corpus name.'
                        },
                        {
                            'flag': '--body',
                            'help': 'Whether to download pages body.',
                            'action': 'store_true'
                        },
                        {
                            'flag': '--password',
                            'help': 'The corpus\'s password if required.'
                        },
                        {
                            'flag': '--statuses',
                            'help': 'Webentity statuses to dump, separated by comma. Possible statuses being "IN", "OUT", "UNDECIDED" and "DISCOVERED".',
                            'type': SplitterType()
                        }
                    ]
                }
            }
        }
    },

    # Mediacloud action subparser
    # -------------------------------------------------------------------------
    'mediacloud': {
        'package': 'minet.cli.mediacloud',
        'action': 'mediacloud_action',
        'title': 'Minet Mediacloud Command',
        'aliases': ['mc'],
        'description': '''
            Commands related to the MIT Mediacloud API v2.
        ''',
        'subparsers': {
            'help': 'Action to perform using the Mediacloud API.',
            'title': 'actions',
            'dest': 'mc_action',
            'common_arguments': [
                {
                    'flags': ['-t', '--token'],
                    'help': 'Mediacloud API token (also called key).',
                    'rc_key': ['mediacloud', 'token'],
                    'action': ConfigAction
                },
                {
                    'flags': ['-o', '--output'],
                    'action': OutputFileAction
                }
            ],
            'commands': {
                'medias': {
                    'title': 'Minet Mediacloud Medias Command',
                    'description': '''
                        Retrieve metadata about a list of Mediacloud medias.
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the Mediacloud media ids.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the searched Mediacloud media ids.',
                            'action': InputFileAction,
                            'dummy_csv_column': 'media'
                        },
                        {
                            'flag': '--feeds',
                            'help': 'If given, path of the CSV file listing media RSS feeds.',
                            'action': OutputFileAction
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--total',
                            'help': 'Total number of medias. Necessary if you want to display a finite progress indicator.',
                            'type': int
                        }
                    ]
                },
                'search': {
                    'title': 'Minet Mediacloud Search Command',
                    'description': '''
                        Search stories on the Mediacloud platform.
                        To learn how to compose more relevant queries, check out this guide:
                        https://mediacloud.org/support/query-guide
                    ''',
                    'arguments': [
                        {
                            'name': 'query',
                            'help': 'Search query.'
                        },
                        {
                            'flags': ['-c', '--collections'],
                            'help': 'List of collection ids to search, separated by commas.',
                            'type': SplitterType()
                        },
                        {
                            'flags': ['--filter-query'],
                            'help': 'Solr filter query `fq` to use. Can be used to optimize some parts of the query.'
                        },
                        {
                            'flags': ['-m', '--medias'],
                            'help': 'List of media ids to search, separated by commas.',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--publish-day',
                            'help': 'Only search stories published on provided day (iso format, e.g. "2018-03-24").'
                        },
                        {
                            'flag': '--publish-month',
                            'help': 'Only search stories published on provided month (iso format, e.g. "2018-03").'
                        },
                        {
                            'flag': '--publish-year',
                            'help': 'Only search stories published on provided year (iso format, e.g. "2018").'
                        },
                        {
                            'flag': '--skip-count',
                            'help': 'Whether to skip the first API call counting the number of posts for the progress bar.',
                            'action': 'store_true'
                        }
                    ]
                },
                'topic': {
                    'title': 'Minet Mediacloud Topic Command',
                    'description': '''
                        Gather information and aggregated stats about pages and groups of
                        the designated dashboard (indicated by a given token).
                    ''',
                    'subparsers': {
                        'help': 'Topic action to perform.',
                        'title': 'topic_actions',
                        'dest': 'mc_topic_action',
                        'commands': {
                            'stories': {
                                'title': 'Minet Mediacloud Topic Stories Command',
                                'description': 'Retrieves the list of stories from a mediacloud topic.',
                                'arguments': [
                                    {
                                        'name': 'topic_id',
                                        'help': 'Id of the topic.'
                                    },
                                    {
                                        'flag': '--media-id',
                                        'help': 'Return only stories belonging to the given media_ids.'
                                    },
                                    {
                                        'flag': '--from-media-id',
                                        'help': 'Return only stories that are linked from stories in the given media_id.'
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
    },

    # Resolve action subparser
    # --------------------------------------------------------------------------
    'resolve': {
        'package': 'minet.cli.resolve',
        'action': 'resolve_action',
        'title': 'Minet Resolve Command',
        'description': '''
            Use multiple threads to resolve batches of urls from a CSV file. The
            command outputs a CSV report with additional metadata about the
            HTTP calls and the followed redirections.
        ''',
        'epilog': '''
            columns being added to the output:

            . "resolved": final resolved url (after solving redirects).
            . "status": HTTP status code of the request, e.g. 200, 404, 503 etc.
            . "error": an error code if anything went wrong when performing the request.
            . "redirects": total number of redirections to reach the final url.
            . "chain": list of redirection types separated by "|".

            examples:

            . Resolving a batch of url from existing CSV file:
                $ minet resolve url_column file.csv > report.csv

            . CSV input from stdin:
                $ xsv select url_column file.csv | minet resolve url_column > report.csv

            . Resolving a single url:
                $ minet resolve https://lemonde.fr
        ''',
        'arguments': [
            {
                'name': 'column',
                'help': 'Column of the CSV file containing urls to resolve or a single url to resolve.'
            },
            {
                'name': 'file',
                'help': 'CSV file containing the urls to resolve.',
                'action': InputFileAction,
                'dummy_csv_column': 'url'
            },
            *FETCH_COMMON_ARGUMENTS,
            {
                'flag': '--max-redirects',
                'help': 'Maximum number of redirections to follow before breaking. Defaults to 20.',
                'type': int,
                'default': DEFAULT_RESOLVE_MAX_REDIRECTS
            },
            {
                'flag': '--follow-meta-refresh',
                'help': 'Whether to follow meta refresh tags. Requires to buffer a bit of the response body, so it will slow things down.',
                'action': 'store_true'
            },
            {
                'flag': '--follow-js-relocation',
                'help': 'Whether to follow typical JavaScript window relocation. Requires to buffer a bit of the response body, so it will slow things down.',
                'action': 'store_true'
            },
            {
                'flag': '--infer-redirection',
                'help': 'Whether to try to heuristically infer redirections from the urls themselves, without requiring a HTTP call.',
                'action': 'store_true'
            },
            {
                'flag': '--only-shortened',
                'help': 'Whether to only attempt to resolve urls that are probably shortened.',
                'action': 'store_true'
            }
        ]
    },

    # Scrape action subparser
    # -------------------------------------------------------------------------
    'scrape': {
        'package': 'minet.cli.scrape',
        'action': 'scrape_action',
        'title': 'Minet Scrape Command',
        'description': '''
            Use multiple processes to scrape data from a batch of HTML files.
            This command can either work on a `minet fetch` report or on a bunch
            of files filtered using a glob pattern.

            It will output the scraped items as a CSV file.
        ''',
        'epilog': '''
            examples:

            . Scraping item from a `minet fetch` report:
                $ minet scrape scraper.yml report.csv > scraped.csv

            . Working on a report from stdin:
                $ minet fetch url_column file.csv | minet scrape scraper.yml > scraped.csv

            . Scraping a single page from the web:
                $ minet fetch https://news.ycombinator.com/ | minet scrape scraper.yml > scraped.csv

            . Scraping items from a bunch of files:
                $ minet scrape scraper.yml --glob "./content/**/*.html" > scraped.csv

            . Yielding items as newline-delimited JSON (jsonl):
                $ minet scrape scraper.yml report.csv --format jsonl > scraped.jsonl

            . Only validating the scraper definition and exit:
                $ minet scraper --validate scraper.yml

            . Using a strainer to optimize performance:
                $ minet scraper links-scraper.yml --strain "a[href]" report.csv > links.csv
        ''',
        'arguments': [
            {
                'name': 'scraper',
                'help': 'Path to a scraper definition file.',
                'type': FileType('r', encoding='utf-8')
            },
            {
                'name': 'report',
                'help': 'Input CSV fetch action report file.',
                'action': InputFileAction
            },
            {
                'flags': ['-f', '--format'],
                'help': 'Output format.',
                'choices': ['csv', 'jsonl'],
                'default': 'csv'
            },
            {
                'flags': ['-g', '--glob'],
                'help': 'Whether to scrape a bunch of html files on disk matched by a glob pattern rather than sourcing them from a CSV report.'
            },
            {
                'flags': ['-i', '--input-dir'],
                'help': 'Directory where the HTML files are stored. Defaults to "%s".' % DEFAULT_CONTENT_FOLDER
            },
            {
                'flags': ['-o', '--output'],
                'action': OutputFileAction
            },
            {
                'flags': ['-p', '--processes'],
                'help': 'Number of processes to use. Defaults to roughly half of the available CPUs.',
                'type': int
            },
            {
                'flag': '--separator',
                'help': 'Separator use to join lists of values when output format is CSV. Defaults to "|".'
            },
            {
                'flag': '--strain',
                'help': 'Optional CSS selector used to strain, i.e. only parse matched tags in the parsed html files in order to optimize performance.'
            },
            {
                'flag': '--total',
                'help': 'Total number of HTML documents. Necessary if you want to display a finite progress indicator.',
                'type': int
            },
            {
                'flag': '--validate',
                'help': 'Just validate the given scraper then exit.',
                'action': 'store_true'
            }
        ]
    },

    # Twitter action subparser
    # -------------------------------------------------------------------------
    'twitter': {
        'package': 'minet.cli.twitter',
        'action': 'twitter_action',
        'aliases': ['tw'],
        'title': 'Minet Twitter Command',
        'description': '''
            Gather data from Twitter.
        ''',
        'subparsers': {
            'help': 'Action to perform.',
            'title': 'actions',
            'dest': 'tw_action',
            'commands': {
                'friends': {
                    'title': 'Minet Twitter Friends Command',
                    'description': '''
                        Retrieve friends, i.e. followed users, of given user.
                    ''',
                    'epilog': '''
                        examples:

                        . Getting friends of a list of user:
                            $ minet tw friends screen_name users.csv > friends.csv
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the Twitter account screen names or ids.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired Twitter users.',
                            'action': InputFileAction,
                            'dummy_csv_column': 'user'
                        },
                        *TWITTER_API_COMMON_ARGUMENTS,
                        {
                            'flag': '--ids',
                            'help': 'Whether your users are given as ids rather than screen names.',
                            'action': 'store_true'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction,
                            'resumer': BatchResumer,
                            'resumer_kwargs': lambda args: ({'value_column': args.column})
                        },
                        {
                            'flag': '--resume',
                            'help': 'Whether to resume from an aborted collection. Need -o to be set.',
                            'action': 'store_true'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--total',
                            'help': 'Total number of accounts. Necessary if you want to display a finite progress indicator.',
                            'type': int
                        }
                    ]
                },
                'followers': {
                    'title': 'Minet Twitter Followers Command',
                    'description': '''
                        Retrieve followers of given user.
                    ''',
                    'epilog': '''
                        examples:

                        . Getting followers of a list of user:
                            $ minet tw followers screen_name users.csv > followers.csv
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the Twitter account screen names or ids.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired Twitter users.',
                            'action': InputFileAction,
                            'dummy_csv_column': 'user'
                        },
                        *TWITTER_API_COMMON_ARGUMENTS,
                        {
                            'flag': '--ids',
                            'help': 'Whether your users are given as ids rather than screen names.',
                            'action': 'store_true'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction,
                            'resumer': BatchResumer,
                            'resumer_kwargs': lambda args: ({'value_column': args.column})
                        },
                        {
                            'flag': '--resume',
                            'help': 'Whether to resume from an aborted collection. Need -o to be set.',
                            'action': 'store_true'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--total',
                            'help': 'Total number of accounts. Necessary if you want to display a finite progress indicator.',
                            'type': int
                        }
                    ]
                },
                'scrape': {
                    'title': 'Minet Twitter Scrape Command',
                    'description': '''
                        Scrape Twitter's public facing search API to collect tweets etc.
                    ''',
                    'epilog': '''
                        examples:

                        . Collecting the latest 500 tweets of a given Twitter user:
                            $ minet tw scrape tweets "from:@jack" --limit 500 > tweets.csv

                        . Collecting the tweets from multiple Twitter queries listed in a CSV file:
                            $ minet tw scrape tweets query queries.csv > tweets.csv

                        . Templating the given CSV column to query tweets by users:
                            $ minet tw scrape tweets user users.csv --query-template 'from:@{value}' > tweets.csv

                        . Avoid to search into usernames or handles by adding a OR @aNotExistingHandle (this is a temporary hack which might be deprecated anytime)
                            $ minet tw scrape tweets "keyword OR @aNotExistingHandle"
                        related discussion: https://webapps.stackexchange.com/questions/127425/how-to-exclude-usernames-and-handles-while-searching-twitter
                    ''',
                    'arguments': [
                        {
                            'name': 'items',
                            'help': 'What to scrape. Currently only `tweets` is possible.',
                            'choices': ['tweets']
                        },
                        {
                            'name': 'query',
                            'help': 'Search query or name of the column containing queries to run in given CSV file.'
                        },
                        {
                            'name': 'file',
                            'help': 'Optional CSV file containing the queries to be run.',
                            'action': InputFileAction,
                            'dummy_csv_column': 'query',
                            'column_dest': 'query'
                        },
                        {
                            'flag': '--include-refs',
                            'help': 'Whether to emit referenced tweets (quoted, retweeted & replied) in the CSV output. Note that it consumes a memory proportional to the total number of unique tweets retrieved.',
                            'action': 'store_true'
                        },
                        {
                            'flags': ['-l', '--limit'],
                            'help': 'Maximum number of tweets to collect per query.',
                            'type': int
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction
                        },
                        {
                            'flag': '--query-template',
                            'help': 'Query template. Can be useful for instance to change a column of twitter user screen names into from:@user queries.'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        }
                    ]
                },
                'users': {
                    'title': 'Minet Twitter Users Command',
                    'description': '''
                        Retrieve Twitter user metadata using the API.
                    ''',
                    'epilog': '''
                        examples:

                        . Getting metadata from an user:
                            $ minet tw users screen_name users.csv > data_users.csv
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the Twitter account screen names or ids.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired Twitter users.',
                            'action': InputFileAction,
                            'dummy_csv_column': 'user'
                        },
                        *TWITTER_API_COMMON_ARGUMENTS,
                        {
                            'flag': '--ids',
                            'help': 'Whether your users are given as ids rather than screen names.',
                            'action': 'store_true'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--total',
                            'help': 'Total number of accounts. Necessary if you want to display a finite progress indicator.',
                            'type': int
                        }
                    ]
                },
                'user-tweets': {
                    'title': 'Minet Twitter User Tweets Command',
                    'description': '''
                        Retrieve the last ~3200 tweets, including retweets from
                        the given Twitter users, using the API.
                    ''',
                    'epilog': '''
                        examples:

                        . Getting tweets from users in a CSV file:
                            $ minet tw user-tweets screen_name users.csv > tweets.csv
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the Twitter account screen names or ids.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired Twitter users.',
                            'action': InputFileAction,
                            'dummy_csv_column': 'user'
                        },
                        *TWITTER_API_COMMON_ARGUMENTS,
                        {
                            'flag': '--ids',
                            'help': 'Whether your users are given as ids rather than screen names.',
                            'action': 'store_true'
                        },
                        {
                            'flag': '--exclude-retweets',
                            'help': 'Whether to exclude retweets from the output.',
                            'action': 'store_true'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'action': OutputFileAction
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--total',
                            'help': 'Total number of accounts. Necessary if you want to display a finite progress indicator.',
                            'type': int
                        }
                    ]
                }
            }
        }
    },

    # Url Extract action subparser
    # -------------------------------------------------------------------------
    'url-extract': {
        'package': 'minet.cli.url_extract',
        'action': 'url_extract_action',
        'title': 'Minet Url Extract Command',
        'description': '''
            Extract urls from a CSV column containing either raw text or raw
            HTML.
        ''',
        'epilog': '''
            examples:

            . Extracting urls from a text column:
                $ minet url-extract text posts.csv > urls.csv

            . Extracting urls from a html column:
                $ minet url-extract html --from html posts.csv > urls.csv
        ''',
        'arguments': [
            {
                'name': 'column',
                'help': 'Name of the column containing text or html.'
            },
            {
                'name': 'file',
                'help': 'Target CSV file.',
                'action': InputFileAction
            },
            {
                'flag': '--base-url',
                'help': 'Base url used to resolve relative urls.'
            },
            {
                'flag': '--from',
                'help': 'Extract urls from which kind of source?',
                'choices': ['text', 'html'],
                'default': 'text'
            },
            {
                'flags': ['-o', '--output'],
                'action': OutputFileAction
            },
            {
                'flags': ['-s', '--select'],
                'help': 'Columns to keep in output, separated by comma.',
                'type': SplitterType()
            },
            {
                'flag': '--total',
                'help': 'Total number of lines in CSV file. Necessary if you want to display a finite progress indicator for large input files.',
                'type': int
            }
        ]
    },

    # Url Join action subparser
    # -------------------------------------------------------------------------
    'url-join': {
        'package': 'minet.cli.url_join',
        'action': 'url_join_action',
        'title': 'Minet Url Join Command',
        'description': '''
            Join two CSV files by matching them on columns containing urls. It
            works by indexing the first file's urls in a specialized
            URL trie to match them with the second file's urls.
        ''',
        'epilog': '''
            examples:

            . Joining two files:
                $ minet url-join url webentities.csv post_url posts.csv > joined.csv

            . Keeping only some columns from first file:
                $ minet url-join url webentities.csv post_url posts.csv -s url,id > joined.csv
        ''',
        'arguments': [
            {
                'name': 'column1',
                'help': 'Name of the column containing urls in the indexed file.'
            },
            {
                'name': 'file1',
                'help': 'Path to the file to index.',
                'action': InputFileAction,
                'nargs': None
            },
            {
                'name': 'column2',
                'help': 'Name of the column containing urls in the second file.'
            },
            {
                'name': 'file2',
                'help': 'Path to the second file.',
                'action': InputFileAction,
                'nargs': None
            },
            {
                'flags': ['-o', '--output'],
                'action': OutputFileAction
            },
            {
                'flags': ['-p', '--match-column-prefix'],
                'help': 'Optional prefix to add to the first file\'s column names to avoid conflicts.',
                'default': ''
            },
            {
                'flags': ['-s', '--select'],
                'help': 'Columns from the first file to keep, separated by comma.'
            },
            {
                'flag': '--separator',
                'help': 'Split indexed url column by a separator?'
            }
        ]
    },

    # Url Parse action subparser
    # -------------------------------------------------------------------------
    'url-parse': {
        'package': 'minet.cli.url_parse',
        'action': 'url_parse_action',
        'title': 'Minet Url Parse Command',
        'description': '''
            Parse the urls contained in a CSV file using the python `ural`
            library to extract useful information about them such as their
            normalized version, domain name, etc.
        ''',
        'epilog': '''
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
            . "probably_shortened": whether the url is probably shortened or
              not (bit.ly, t.co etc.).

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
        ''',
        'arguments': [
            {
                'name': 'column',
                'help': 'Name of the column containing urls.'
            },
            {
                'name': 'file',
                'help': 'Target CSV file.',
                'action': InputFileAction
            },
            {
                'flag': '--facebook',
                'help': 'Whether to consider and parse the given urls as coming from Facebook.',
                'action': 'store_true'
            },
            {
                'flags': ['-o', '--output'],
                'action': OutputFileAction
            },
            {
                'flags': ['-s', '--select'],
                'help': 'Columns to keep in output, separated by comma.',
                'type': SplitterType()
            },
            {
                'flag': '--separator',
                'help': 'Split url column by a separator?'
            },
            {
                'flags': ['--strip-protocol', '--no-strip-protocol'],
                'help': 'Whether or not to strip the protocol when normalizing the url. Defaults to strip protocol.',
                'dest': 'strip_protocol',
                'action': BooleanAction,
                'default': True
            },
            {
                'flag': '--total',
                'help': 'Total number of lines in CSV file. Necessary if you want to display a finite progress indicator for large input files.',
                'type': int
            },
            {
                'flag': '--youtube',
                'help': 'Whether to consider and parse the given urls as coming from YouTube.',
                'action': 'store_true'
            }
        ]
    },

    # Youtube action subparser
    # --------------------------------------------------------------------------
    'youtube': {
        'package': 'minet.cli.youtube',
        'action': 'youtube_action',
        'aliases': ['yt'],
        'title': 'Minet Youtube command',
        'description': '''
            Gather data from Youtube.
        ''',
        'subparsers': {
            'help': 'Actions to perform on Youtube.',
            'title': 'actions',
            'dest': 'yt_action',
            'common_arguments': [
                {
                    'flags': ['-o', '--output'],
                    'action': OutputFileAction
                }
            ],
            'commands': {
                'captions': {
                    'title': 'Youtube captions',
                    'description': 'Retrieve captions for the given YouTube videos.',
                    'epilog': '''
                        examples:

                        . Fetching captions for a list of videos:
                            $ minet yt captions video_id videos.csv > captions.csv

                        . Fetching French captions with a fallback to English:
                            $ minet yt captions video_id videos.csv --lang fr,en > captions.csv
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the video urls or ids.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the Youtube video urls or ids.',
                            'action': InputFileAction,
                            'dummy_csv_column': 'video'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--lang',
                            'help': 'Language (ISO code like "en") of captions to retrieve. You can specify several languages by preferred order separated by commas. Defaults to "en".',
                            'default': ['en'],
                            'type': SplitterType()
                        },
                    ]
                },
                'comments': {
                    'title': 'Youtube comments',
                    'description': 'Retrieve metadata about Youtube comments using the API.',
                    'epilog': '''
                        example:

                        . Fetching a video's comments:
                            $ minet yt comments https://www.youtube.com/watch?v=7JTb2vf1OQQ -k my-api-key > comments.csv
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'This argument can either take the name of the column containing the video\'s id/url if a file is passed as an argument, or a single youtube video\'s id/url if there is no file '
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the Youtube videos ids.',
                            'action': InputFileAction,
                            'dummy_csv_column': 'video'
                        },
                        {
                            'flags': ['-k', '--key'],
                            'help': 'YouTube API Data dashboard API key.',
                            'rc_key': ['youtube', 'key'],
                            'action': ConfigAction
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        }
                    ]
                },
                'search': {
                    'title': 'Youtube search',
                    'description': 'Retrieve metadata about Youtube search field using the API.',
                    'epilog': '''
                        example:

                        . Searching videos about birds:
                            $ minet youtube search bird -k my-api-key > bird_videos.csv
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'This argument can either take the query on which we want to retrieve videos from the API or the name of the column containing that query'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the query for youtube Search.',
                            'action': InputFileAction,
                            'dummy_csv_column': 'query'
                        },
                        {
                            'flags': ['-k', '--key'],
                            'help': 'YouTube API Data dashboard API key.',
                            'rc_key': ['youtube', 'key'],
                            'action': ConfigAction
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flags': ['-l', '--limit'],
                            'help': 'Maximum number of videos to retrieve per query.',
                            'type': int
                        },
                        {
                            'flags': ['--order'],
                            'help': 'Order in which videos are retrieved. The default one is relevance.',
                            'default': YOUTUBE_API_DEFAULT_SEARCH_ORDER,
                            'choices': YOUTUBE_API_SEARCH_ORDERS
                        }
                    ]
                },
                'videos': {
                    'title': 'Youtube videos',
                    'description': 'Retrieve metadata about Youtube videos using the API.',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the video\'s urls or ids.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the Youtube videos urls or ids.',
                            'action': InputFileAction,
                            'dummy_csv_column': 'video'
                        },
                        {
                            'flags': ['-k', '--key'],
                            'help': 'YouTube API Data dashboard API key.',
                            'rc_key': ['youtube', 'key'],
                            'action': ConfigAction
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns of input CSV file to include in the output (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--total',
                            'help': 'Total number of videos. Necessary if you want to display a finite progress indicator.',
                            'type': int
                        }
                    ]
                }
            }
        }
    }
}
