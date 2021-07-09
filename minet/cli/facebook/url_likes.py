# =============================================================================
# Minet Facebook Url Likes CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving approximate
# likes count by scraping Facebook's like button plugin.
#
import re
import casanova
from urllib.parse import quote
from ural import is_url

from minet.utils import rate_limited
from minet.web import request
from minet.cli.utils import die, LoadingBar

REPORT_HEADERS = ['approx_likes', 'approx_likes_int']
NUMBER_RE = re.compile(rb'>(\d+\.?\d*[KM]?)<', re.I)


def forge_url(url):
    return 'https://www.facebook.com/plugins/share_button.php?href=%s&layout=button_count' % quote(url)


@rate_limited(5)
def make_request(url):
    err, response = request(forge_url(url), headers={'Accept-Language': 'en'})

    if response.status == 404:
        return 'not-found', None

    if err:
        return 'http-error', None

    return err, response.data


def scrape(data):

    match = NUMBER_RE.search(data)

    if match is None:
        return ['', '']

    approx_likes = match.group(1).decode()
    approx_likes_int = approx_likes

    if 'K' in approx_likes:
        approx_likes_int = str(int(float(approx_likes[:-1]) * 10**3))

    elif 'M' in approx_likes:
        approx_likes_int = str(int(float(approx_likes[:-1]) * 10**6))

    return [approx_likes, approx_likes_int]


def facebook_url_likes_action(cli_args):
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=REPORT_HEADERS,
        total=cli_args.total
    )

    if cli_args.column not in enricher.headers:
        die([
            'Could not find the "%s" column containing the urls in the given CSV file.' % cli_args.column
        ])

    loading_bar = LoadingBar(
        desc='Retrieving likes',
        unit='url',
        total=enricher.total
    )

    for row, url in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.update()

        url = url.strip()

        if not url or not is_url(url, require_protocol=False):
            enricher.writerow(row)
            continue

        err, html = make_request(url)

        if err is not None:
            loading_bar.die('An error occurred while fetching like button for this url: %s' % url)

        scraped = scrape(html)

        if scraped is None:
            loading_bar.die('Could not extract Facebook likes from this url\'s like button: %s' % url)

        enricher.writerow(row, scraped)
