# =============================================================================
# Minet Facebook Url Likes CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving approximate
# likes count by scraping Facebook's like button plugin.
#
import casanova
import re
from tqdm import tqdm
from urllib.parse import quote
from minet.utils import create_pool, request, rate_limited
from minet.cli.utils import open_output_file, die

REPORT_HEADERS = ['approx_likes', 'approx_likes_int']
GET_LIKE_RE = re.compile(r'<span>\d.{0,7}[KM\d]\s+people')


def forge_url(url):
    url_base = "https://www.facebook.com/plugins/like.php?href=" + quote(url)
    return url_base


def get_approx_number(nb):
    nb = nb.strip()
    final_nb = ""
    has_comma = False
    for x in nb:
        if x == ".":
            has_comma = True
            continue
        if x == "K":
            if has_comma:
                final_nb = int(final_nb) * 100
            else:
                final_nb = int(final_nb) * 1000
            return final_nb
        if x == "M":
            if has_comma:
                final_nb = int(final_nb) * 100000
            else:
                final_nb = int(final_nb) * 1000000
            return final_nb
        else:
            final_nb += x
    return nb

@rate_limited(5,1)
def make_request(http, url):
    err, response = request(http, forge_url(url), headers={'Accept-Language': 'en'})

    if err:
        return 'http-error', None

    if response.status == 404:
        return 'not-found', None

    if response.status >= 400:
        return 'http-error', None

    return (err, response.data)


def fetch_approxes(err, data, url):
    if err:
        die('Request error : we could not get the number of likes for this url')
    try:
        raw = GET_LIKE_RE.search(data.decode())
        raw_fetch = raw.group()[6:]
        raw_approx = ""
        for charact in raw_fetch:
            try:
                nb_approx = int(charact)
                raw_approx += charact
            except:
                if charact == "K" or charact == "M" or charact == ".":
                    raw_approx += charact
                else:
                    pass
        precise_approx = get_approx_number(raw_approx)
    except:
        die('Facebook error : could not get the number of likes for this url :' + url)
    return raw_approx, precise_approx


def facebook_url_likes_action(namespace):
    output_file = open_output_file(namespace.output)

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
    )

    http = create_pool()

    for row, url in enricher.cells(namespace.column, with_rows=True):

        loading_bar.update()

        url_data = url.strip()

        data = make_request(http, url_data)

        results = fetch_approxes(data[0], data[1], url_data)

        enricher.writerow(row, [results[0], results[1]])
