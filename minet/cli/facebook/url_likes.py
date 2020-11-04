# =============================================================================
# Minet Facebook Url Likes CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving approximate
# likes count by scraping Facebook's like button plugin.
#
import casanova
from tqdm import tqdm
from urllib.parse import quote
from minet.utils import create_pool, request
from minet.cli.utils import open_output_file, die
import time
import re
from bs4 import BeautifulSoup

REPORT_HEADERS = ['approx_likes', 'approx_likes_int']
GET_LIKE_RE_FR = re.compile(r'[\d\.KM]*')

#### - my part -- ###

### - encode url #### 
def forge_url(url):
    url_base = "https://www.facebook.com/plugins/like.php?href=" + quote(url)
    return url_base

### get the int approx : 
def get_approx_number(nb):
    nb = nb.strip()
    final_nb = ""
    is_comma = False
    for x in nb:
        if x ==".":
            is_comma = True
            continue
        if x =="K":
            if is_comma:
                final_nb = int(final_nb)*100
            else:
                final_nb = int(final_nb)*1000
            return final_nb
        if x=="M":
            if  is_comma:
                final_nb = int(final_nb)*100000
            else:
                final_nb = int(final_nb)*1000000
            return final_nb
        else:
            final_nb += x
    return nb

### Fetch approximations


def make_request(http,url):
    time.sleep(0.05)

    err, response = request(http, forge_url(url),  headers={'Accept-Language': 'en'})

    if err:
        return 'http-error', None

    if response.status == 404:
        return 'not-found', None

    if response.status >= 400:
        return 'http-error', None

    return response.data

def fetch_approxes(data):

    soup_page1 = BeautifulSoup(data, "lxml")
    appr_likes = soup_page1.select("span#u_0_3 > span:first-child")[0].string
    try:
        raw = GET_LIKE_RE_FR.search(appr_likes)
        raw_approx = raw.group()
        precise_approx = get_approx_number(raw_approx)
    except:
        die('could not get the number of likes for ' % url)
    return raw_approx,precise_approx


#### --------#####

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

        results = fetch_approxes(data)

        enricher.writerow(row, [results[0], results[1]])
