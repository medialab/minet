# =============================================================================
# Minet CLI Commands Definition
# =============================================================================
#
# Defining every minet command.
#
import sys
from argparse import FileType

from minet.constants import DEFAULT_THROTTLE
from minet.cli.defaults import DEFAULT_CONTENT_FOLDER
from minet.cli.utils import die
from minet.cli.argparse import (
    BooleanAction,
    ConfigAction,
    SplitterType
)

from minet.crowdtangle.constants import (
    CROWDTANGLE_SORT_TYPES,
    CROWDTANGLE_SUMMARY_SORT_TYPES,
    CROWDTANGLE_DEFAULT_RATE_LIMIT
)


def check_dragnet():
    try:
        import dragnet
    except:
        die([
            'The `dragnet` library is not installed. The `extract` command won\'t work.',
            'To install it correctly, run the following commands in order:',
            '',
            '  pip install lxml numpy Cython',
            '  pip install dragnet'
        ])


MINET_COMMANDS = {

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

            . TODO:
                `minet crawl`
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
                    'flags': ['-o', '--output'],
                    'help': 'Path to the output file. By default, everything will be printed to stdout.'
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
                        Gather information and aggregated stats about pages and groups of
                        the designated dashboard (indicated by a given token).
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching accounts statistics for every account in your dashboard:
                            `minet ct leaderboard --token YOUR_TOKEN > accounts-stats.csv`
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
                        }
                    ]
                },
                'lists': {
                    'title': 'Minet CrowdTangle Lists Command',
                    'description': '''
                        Retrieve the lists from a CrowdTangle dashboard (indicated by a
                        given token).
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching a dashboard's lists:
                            `minet ct lists --token YOUR_TOKEN > lists.csv`
                    '''
                },
                'posts': {
                    'title': 'Minet CrowdTangle Posts Command',
                    'description': '''
                        Gather post data from the designated dashboard (indicated by
                        a given token).
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching the 500 most latest posts from a dashboard:
                            `minet ct posts --token YOUR_TOKEN --limit 500 > latest-posts.csv`
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
                            'help': 'The earliest date at which a post could be posted (UTC!). You can pass just a year or a year-month for convenience.'
                        }
                    ]
                },
                'posts-by-id': {
                    'title': 'Minet CrowdTangle Post By Id Command',
                    'description': '''
                        Retrieve metadata about batches of posts using Crowdtangle's API.
                    ''',
                    'epilog': '''
                        examples:

                        . Retrieving information about a batch of posts:
                            `minet ct posts-by-id post-url posts.csv --token YOUR_TOKEN > metadata.csv`

                        . Retrieving information about a single post:
                            `minet ct posts-by-id 1784333048289665 --token YOUR_TOKEN`
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the posts URL or id in the CSV file.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired URLs or ids.',
                            'type': FileType('r'),
                            'default': sys.stdin,
                            'nargs': '?'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns to include in report (separated by `,`).',
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

                        More on Crowdtangle API docs here:
                        https://github.com/CrowdTangle/API/wiki/Search
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching a dashboard's lists:
                            `minet ct search --token YOUR_TOKEN > posts.csv`
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
                            'flags': ['-p', '--platforms'],
                            'help': 'The platforms from which to retrieve links (facebook, instagram, or reddit). This value can be comma-separated.',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--sort-by',
                            'help': 'The order in which to retrieve posts. Defaults to `date`.',
                            'choices': CROWDTANGLE_SORT_TYPES,
                            'default': 'date'
                        },
                        {
                            'flag': '--start-date',
                            'help': 'The earliest date at which a post could be posted (UTC!). You can pass just a year or a year-month for convenience.'
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
                        Retrieve aggregated statistics about link sharing
                        on the Crowdtangle API and by platform.
                    ''',
                    'epilog': '''
                        examples:

                        . Computing a summary of aggregated stats for urls contained in a CSV row:
                            `minet ct summary url urls.csv --token YOUR_TOKEN --start-date 2019-01-01 > summary.csv`
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the URL in the CSV file.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired URLs.',
                            'type': FileType('r'),
                            'default': sys.stdin,
                            'nargs': '?'
                        },
                        {
                            'flags': ['-p', '--platforms'],
                            'help': 'The platforms from which to retrieve links (facebook, instagram, or reddit). This value can be comma-separated.',
                            'type': SplitterType()
                        },
                        {
                            'name': '--posts',
                            'help': 'Path to a file containing the retrieved posts.',
                            'type': FileType('w')
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns to include in report (separated by `,`).'
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
                    'help': 'Path to the output report file. By default, the report will be printed to stdout.'
                }
            ],
            'commands': {
                'captions': {
                    'title': 'Youtube captions',
                    'description': 'Retrieve metadata about Youtube captions.',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the video\'s url or id.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the Youtube videos urls or ids.',
                            'type': FileType('r'),
                            'default': sys.stdin,
                            'nargs': '?'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns to include in report (separated by `,`).'
                        },
                        {
                            'flag': '--lang',
                            'help': 'Language (ISO code like "fr") of captions to retrieve.',
                            'default': 'en'
                        },
                    ]
                },
                'comments': {
                    'title': 'Youtube comments',
                    'description': 'Retrieve metadata about Youtube comments using the API.',
                    'arguments': [
                        {
                            'name': 'id',
                            'help': 'Youtube video\'s id.',
                        },
                        {
                            'flags': ['-k', '--key'],
                            'help': 'YouTube API Data dashboard API key.'
                        }
                    ]
                },
                'url-parse': {
                    'title': 'Parse Youtube URLs',
                    'description': 'Extract informations from Youtube URLs',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the URL in the CSV file.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired URLs.',
                            'type': FileType('r'),
                            'default': sys.stdin,
                            'nargs': '?'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns to include in report (separated by `,`).'
                        }
                    ]
                },
                'videos': {
                    'title': 'Youtube videos',
                    'description': 'Retrieve metadata about Youtube videos using the API.',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the video\'s url or id.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the Youtube videos urls or ids.',
                            'type': FileType('r'),
                            'default': sys.stdin,
                            'nargs': '?'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns to include in report (separated by `,`).'
                        },
                        {
                            'flags': ['-k', '--key'],
                            'help': 'YouTube API Data dashboard API key.'
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
            Use multiple processes to extract raw text from a batch of HTML files.
            This command can either work on a `minet fetch` report or on a bunch
            of files. It will output an augmented report with the extracted text.
        ''',
        'epilog': '''
            examples:

            . Extracting raw text from a `minet fetch` report:
                `minet extract report.csv > extracted.csv`

            . Working on a report from stdin:
                `minet fetch url_column file.csv | minet extract > extracted.csv`

            . Extracting raw text from a bunch of files:
                `minet extract --glob "./content/*.html" > extracted.csv`
        ''',
        'before': check_dragnet,
        'arguments': [
            {
                'name': 'report',
                'help': 'Input CSV fetch action report file.',
                'type': FileType('r'),
                'default': sys.stdin,
                'nargs': '?'
            },
            {
                'flags': ['-e', '--extractor'],
                'help': 'Extraction engine to use. Defaults to `dragnet`.',
                'choices': ['dragnet', 'html2text']
            },
            {
                'flags': ['-i', '--input-directory'],
                'help': 'Directory where the HTML files are stored. Defaults to "%s".' % DEFAULT_CONTENT_FOLDER,
                'default': DEFAULT_CONTENT_FOLDER
            },
            {
                'flags': ['-o', '--output'],
                'help': 'Path to the output report file. By default, the report will be printed to stdout.'
            },
            {
                'flags': ['-p', '--processes'],
                'help': 'Number of processes to use. Defaults to 4.',
                'type': int,
                'default': 4
            },
            {
                'flags': ['-s', '--select'],
                'help': 'Columns to include in report (separated by `,`).',
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
                        Scrape series of comments on Facebook.
                    ''',
                    'epilog': '''
                        examples:

                        . Fetching a post's comments:
                            `minet fb comments -c firefox https://www.facebook.com/page/posts/3601645349798293 > comments.csv`
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Column of the CSV file containing post urls or a single post url to fetch.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the post urls.',
                            'type': FileType('r'),
                            'default': sys.stdin,
                            'nargs': '?'
                        },
                        {
                            'flags': ['-c', '--cookie'],
                            'help': 'Authenticated cookie to use or browser from which to extract it (support "firefox" and "chrome"). Defaults to "firefox".',
                            'default': 'firefox'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'help': 'Path to the output report file. By default, the report will be printed to stdout.'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns to include in report (separated by `,`).',
                            'type': SplitterType()
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
                            `minet fb post-stats post_url fb-posts.csv`
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the CSV column containing the posts\' urls.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the posts.',
                            'type': FileType('r'),
                            'default': sys.stdin,
                            'nargs': '?'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'help': 'Path to the output report file. By default, the report will be printed to stdout.'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns to include in report (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--total',
                            'help': 'Total number of lines in CSV file. Necessary if you want to display a finite progress indicator.',
                            'type': int
                        }
                    ]
                },
                'url-likes': {
                    'title': 'Retrieve approximate number of likes for the given URLs.',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the URL in the CSV file or a single url.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired URLs.',
                            'type': FileType('r'),
                            'default': sys.stdin,
                            'nargs': '?'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'help': 'Path to the output report file. By default, the report will be printed to stdout.'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns to include in report (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--total',
                            'help': 'Total number of lines in CSV file. Necessary if you want to display a finite progress indicator.',
                            'type': int
                        }
                    ]
                },
                'url-parse': {
                    'title': 'Parse Facebook URLs',
                    'description': 'Extract informations from Facebook URLs.',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the URL in the CSV file.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired URLs.',
                            'type': FileType('r'),
                            'default': sys.stdin,
                            'nargs': '?'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'help': 'Path to the output report file. By default, the report will be printed to stdout.'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns to include in report (separated by `,`).',
                            'type': SplitterType()
                        }
                    ]
                },
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
            examples:

            . Fetching a batch of url from existing CSV file:
                `minet fetch url_column file.csv > report.csv`

            . CSV input from stdin:
                `xsv select url_column file.csv | minet fetch url_column > report.csv`

            . Fetching a single url, useful to pipe into `minet scrape`:
                `minet fetch http://google.com | minet scrape ./scrape.json > scraped.csv`
        ''',
        'arguments': [
            {
                'name': 'column',
                'help': 'Column of the CSV file containing urls to fetch or a single url to fetch.'
            },
            {
                'name': 'file',
                'help': 'CSV file containing the urls to fetch.',
                'type': FileType('r'),
                'default': sys.stdin,
                'nargs': '?'
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
                'flag': '--domain-parallelism',
                'help': 'Max number of urls per domain to hit at the same time. Defaults to 1',
                'type': int,
                'default': 1
            },
            {
                'flags': ['-f', '--filename'],
                'help': 'Name of the column used to build retrieved file names. Defaults to an uuid v4 with correct extension.'
            },
            {
                'flag': '--filename-template',
                'help': 'A template for the name of the fetched files.'
            },
            {
                'flags': ['-g', '--grab-cookies'],
                'help': 'Whether to attempt to grab cookies from your computer\'s browser.',
                'choices': ['firefox', 'chrome']
            },
            {
                'flags': ['-H', '--header'],
                'help': 'Custom headers used with every requests.',
                'action': 'append',
                'dest': 'headers'
            },
            {
                'flag': '--resume',
                'help': 'Whether to resume from an aborted report.',
                'action': 'store_true'
            },
            {
                'flag': '--standardize-encoding',
                'help': 'Whether to systematically convert retrieved text to UTF-8.',
                'action': 'store_true'
            },
            {
                'flags': ['-o', '--output'],
                'help': 'Path to the output report file. By default, the report will be printed to stdout.'
            },
            {
                'flags': ['-s', '--select'],
                'help': 'Columns to include in report (separated by `,`).',
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
                'help': 'Total number of lines in CSV file. Necessary if you want to display a finite progress indicator.',
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
                            `minet hyphe dump http://myhyphe.com/api/ corpus-name -d corpus`
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
                    'help': 'Path to the output report file. By default, the report will be printed to stdout.'
                }
            ],
            'commands': {
                'search': {
                    'title': 'Minet Mediacloud Search Command',
                    'description': '''
                        Search stories on the Mediacloud platform.
                    ''',
                    'arguments': [
                        {
                            'name': 'query',
                            'help': 'Search query.'
                        },
                        {
                            'flags': ['-c', '--collections'],
                            'help': 'List of searched collections separated by commas.',
                            'type': SplitterType()
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

    # Scrape action subparser
    # -------------------------------------------------------------------------
    'scrape': {
        'package': 'minet.cli.scrape',
        'action': 'scrape_action',
        'title': 'Minet Scrape Command',
        'description': '''
            Use multiple processes to scrape data from a batch of HTML files.
            This command can either work on a `minet fetch` report or on a bunch
            of files. It will output the scraped items.
        ''',
        'epilog': '''
            examples:

            . Scraping item from a `minet fetch` report:
                `minet scrape scraper.json report.csv > scraped.csv`

            . Working on a report from stdin:
                `minet fetch url_column file.csv | minet scrape scraper.json > scraped.csv`

            . Scraping a single page from the web:
                `minet fetch https://news.ycombinator.com/ | minet scrape scraper.json > scraped.csv`

            . Scraping items from a bunch of files:
                `minet scrape scraper.json --glob "./content/*.html" > scraped.csv`
        ''',
        'arguments': [
            {
                'name': 'scraper',
                'help': 'Path to a scraper definition file.',
                'type': FileType('r')
            },
            {
                'name': 'report',
                'help': 'Input CSV fetch action report file.',
                'type': FileType('r'),
                'default': sys.stdin,
                'nargs': '?'
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
                'flags': ['-i', '--input-directory'],
                'help': 'Directory where the HTML files are stored. Defaults to "%s".' % DEFAULT_CONTENT_FOLDER,
                'default': DEFAULT_CONTENT_FOLDER
            },
            {
                'flags': ['-o', '--output'],
                'help': 'Path to the output report file. By default, the report will be printed to stdout.'
            },
            {
                'flags': ['-p', '--processes'],
                'help': 'Number of processes to use. Defaults to 4.',
                'type': int,
                'default': 4
            },
            {
                'flag': '--total',
                'help': 'Total number of HTML documents. Necessary if you want to display a finite progress indicator.',
                'type': int
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
            'help': 'Action to perform using the Twitter API.',
            'title': 'actions',
            'dest': 'tw_action',
            'common_arguments': [
                {
                    'flag': '--api-key',
                    'help': 'Twitter API key.'
                },
                {
                    'flag': '--api-secret-key',
                    'help': 'Twitter API secret key.'
                },
                {
                    'flag': '--access-token',
                    'help': 'Twitter API access token.'
                },
                {
                    'flag': '--access-token-secret',
                    'help': 'Twitter API access token secret.'
                }
            ],
            'commands': {
                'friends': {
                    'title': 'Minet Twitter Friends Command',
                    'description': '''
                        Retrieve friends, i.e. followed users, of given user.
                    ''',
                    'epilog': '''
                        examples:

                        . Getting friends of a list of user:
                            `minet tw friends screen_name users.csv > friends.csv`
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the Twitter account screen names.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired Twitter users.',
                            'type': FileType('r'),
                            'default': sys.stdin,
                            'nargs': '?'
                        },
                        {
                            'flag': '--id',
                            'help': 'Whether to use Twitter user ids rather than screen names.',
                            'action': 'store_true'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'help': 'Path to the output file. By default, the result will be printed to stdout.'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns to include in report (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--resume',
                            'help': 'Whether to resume an aborted collection.',
                            'action': 'store_true'
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
                            `minet tw friends screen_name users.csv > followers.csv`
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the Twitter account screen names.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired Twitter users.',
                            'type': FileType('r'),
                            'default': sys.stdin,
                            'nargs': '?'
                        },
                        {
                            'flag': '--id',
                            'help': 'Whether to use Twitter user ids rather than screen names.',
                            'action': 'store_true'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'help': 'Path to the output file. By default, the result will be printed to stdout.'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns to include in report (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--resume',
                            'help': 'Whether to resume an aborted collection.',
                            'action': 'store_true'
                        },
                        {
                            'flag': '--total',
                            'help': 'Total number of accounts. Necessary if you want to display a finite progress indicator.',
                            'type': int
                        }
                    ]
                },
                'users': {
                    'title': 'Minet Twitter Users Command',
                    'description': '''
                        Retrieve metadata from a given user.
                    ''',
                    'epilog': '''
                        examples:

                        . Getting metadata from an user:
                            `minet tw users screen_name users.csv > data_users.csv`
                    ''',
                    'arguments': [
                        {
                            'name': 'column',
                            'help': 'Name of the column containing the Twitter account screen names.'
                        },
                        {
                            'name': 'file',
                            'help': 'CSV file containing the inquired Twitter users.',
                            'type': FileType('r'),
                            'default': sys.stdin,
                            'nargs': '?'
                        },
                        {
                            'flag': '--id',
                            'help': 'Whether to use Twitter user ids rather than screen names.',
                            'action': 'store_true'
                        },
                        {
                            'flags': ['-o', '--output'],
                            'help': 'Path to the output file. By default, the result will be printed to stdout.'
                        },
                        {
                            'flags': ['-s', '--select'],
                            'help': 'Columns to include in report (separated by `,`).',
                            'type': SplitterType()
                        },
                        {
                            'flag': '--resume',
                            'help': 'Whether to resume an aborted collection.',
                            'action': 'store_true'
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
                `minet url-extract text posts.csv > urls.csv`

            . Extracting urls from a html column:
                `minet url-extract html --from html posts.csv > urls.csv`
        ''',
        'arguments': [
            {
                'name': 'column',
                'help': 'Name of the column containing text or html.'
            },
            {
                'name': 'file',
                'help': 'Target CSV file.',
                'type': FileType('r'),
                'default': sys.stdin,
                'nargs': '?'
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
                'help': 'Path to the output file. By default, the result will be printed to stdout.'
            },
            {
                'flags': ['-s', '--select'],
                'help': 'Columns to keep in output, separated by comma.'
            },
            {
                'flag': '--total',
                'help': 'Total number of lines in CSV file. Necessary if you want to display a finite progress indicator.',
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
            Join two CSV files by matching them on columns containing urls. In
            fact, the command will index the first file's urls into a
            hierchical trie before attempting to match the second file's ones.
        ''',
        'epilog': '''
            examples:

            . Joining two files:
                `minet url-join url webentities.csv post_url posts.csv > joined.csv`

            . Keeping only some columns from first file:
                `minet url-join url webentities.csv post_url posts.csv -s url,id > joined.csv`
        ''',
        'arguments': [
            {
                'name': 'column1',
                'help': 'Name of the url column in the first file.'
            },
            {
                'name': 'file1',
                'help': 'Path to the first file.',
                'type': FileType('r')
            },
            {
                'name': 'column2',
                'help': 'Name of the url column in the second file.'
            },
            {
                'name': 'file2',
                'help': 'Path to the second file.',
                'type': FileType('r')
            },
            {
                'flags': ['-o', '--output'],
                'help': 'Path to the output joined file. By default, the join will be printed to stdout.'
            },
            {
                'flags': ['-s', '--select'],
                'help': 'Columns from the first file to keep, separated by comma.'
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
            Overload a CSV file containing urls with a selection of additional
            metadata such as their normalized version, domain name etc.
        ''',
        'epilog': '''
            examples:

            . Creating a report about a file's urls:
                `minet url-report url posts.csv > report.csv`

            . Keeping only selected columns from the input file:
                `minet url-report url posts.csv -s id,url,title > report.csv`

            . Multiple urls joined by separator:
                `minet url-report urls posts.csv --separator "|" > report.csv`
        ''',
        'arguments': [
            {
                'name': 'column',
                'help': 'Name of the column containing urls.'
            },
            {
                'name': 'file',
                'help': 'Target CSV file.',
                'type': FileType('r'),
                'default': sys.stdin,
                'nargs': '?'
            },
            {
                'flags': ['-o', '--output'],
                'help': 'Path to the output file. By default, the result will be printed to stdout.'
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
                'help': 'Total number of lines in CSV file. Necessary if you want to display a finite progress indicator.',
                'type': int
            }
        ]
    }
}
