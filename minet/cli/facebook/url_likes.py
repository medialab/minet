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

#### - my part -- ###

### - encode url #### 
def enc(url):
    url_base = "https://www.facebook.com/plugins/like.php?href=" + quote(url)
    return url_base

### get the int approx : 
def get_approx_number(nb):
    nb = nb.strip()
    final_nb = ""
    is_coma = False
    if nb[-1]=="K":
        for x in nb:
            if x ==",":
                is_coma = True
                continue
            if x =="K":
                if is_coma:
                    final_nb = int(final_nb)*100
                else:
                    final_nb = int(final_nb)*1000
                return final_nb
            else:
                final_nb += x

    if nb[-1]=="M":
        for x in nb:
            if x ==",":
                is_coma = True
                continue
            if x =="M":
                if not is_coma:
                    final_nb = int(final_nb)*100000
                else:
                    final_nb = int(final_nb)*1000000
                return final_nb
            else:
                final_nb += x
    return nb

### Fetch approximations
http = create_pool()

def Fetch_approxes(url):
   
    time.sleep(0.05)

    err, response = request(http, enc(url))

    if err:
        return 'http-error', None

    if response.status == 404:
        return 'not-found', None

    if response.status >= 400:
        return 'http-error', None

    html = response.data
    soup_page1 = BeautifulSoup(html, "lxml")
    appr_likes = soup_page1.select("span.hidden_elem")[0].string
    try:
        approx1 = re.findall("(?<=et)(.*)(?=autres)",appr_likes)[0]
        pre = get_approx_number(approx1)
    except:
        approx1 = appr_likes
        pre = appr_likes
    return(approx1,pre)


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

    for row, url in enricher.cells(namespace.column, with_rows=True):

        loading_bar.update()

        url_data = url.strip()
      
        results = Fetch_approxes(url_data)

        enricher.writerow(row, [results[0], results[1]])
