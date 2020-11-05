# =============================================================================
# Minet Facebook Url Likes CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving approximate
# likes count by scraping Facebook's like button plugin.
#
import re
import casanova
from tqdm import tqdm
from io import StringIO
from urllib.parse import quote
from ural import is_url

from minet.utils import create_pool, request, rate_limited
from minet.cli.utils import open_output_file, die

REPORT_HEADERS = ['approx_likes', 'approx_likes_int']
NO_LIKES_RE = re.compile(rb'>\s*You like this\.', re.I)
LIKES_RE = re.compile(rb'>\s*([\d.KM]+)\s+people\s+like', re.I)


def forge_url(url):
    return 'https://www.facebook.com/plugins/like.php?href=%s' % quote(url)


@rate_limited(5)
def make_request(http, url):
    err, response = request(http, forge_url(url), headers={'Accept-Language': 'en'})

    if response.status == 404:
        return 'not-found', None

    if err:
        return 'http-error', None

    return err, response.data


def parse_approx_likes(approx_likes, unit='K'):
    multiplier = 1000

    if unit == 'M':
        multiplier = 1000000

    return str(int(float(approx_likes[:-1]) * multiplier))


def scrape(data):
    if NO_LIKES_RE.search(data):
        return ['0', '0']

    match = LIKES_RE.search(data)

    if match is None:
        return ['', '']

    approx_likes = match.group(1).decode()
    approx_likes_int = approx_likes

    if 'K' in approx_likes:
        approx_likes_int = parse_approx_likes(approx_likes, unit='K')

    elif 'M' in approx_likes:
        approx_likes_int = parse_approx_likes(approx_likes, unit='M')

    return [approx_likes, approx_likes_int]


def facebook_url_likes_action(namespace):
    output_file = open_output_file(namespace.output)

    if is_url(namespace.column):
        namespace.file = StringIO('url\n%s' % (namespace.column))
        namespace.column = 'url'

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        keep=namespace.select,
        add=REPORT_HEADERS
    )

    if namespace.column not in enricher.pos:
        die([
            'Could not find the "%s" column containing the urls in the given CSV file.' % namespace.column
        ])

    loading_bar = tqdm(
        desc='Retrieving likes',
        dynamic_ncols=True,
        unit=' urls',
        total=namespace.total
    )

    http = create_pool()

    for row, url in enricher.cells(namespace.column, with_rows=True):
        loading_bar.update()

        url = url.strip()

        err, html = make_request(http, url)

        if err is not None:
            loading_bar.close()
            die('An error occurred while fetching like button for this url: %s' % url)

        scraped = scrape(html)

        if scraped is None:
            loading_bar.close()
            die('Could not extract Facebook likes from this url\'s like button: %s' % url)

        enricher.writerow(row, scraped)
