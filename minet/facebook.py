# =============================================================================
# Minet Facebook Mining Function
# =============================================================================
#
# A function fetching number of Facebook shares of a given url.
#
import re
from bs4 import BeautifulSoup
from urllib.parse import quote
import urllib3
urllib3.disable_warnings()
from ural import strip_protocol


def format_button_result(string):
    string = re.sub(r'\s', '', string)
    string = re.sub(r',', '.', string)
    try:
        digits = string.split('.')
        if len(digits) > 1:
            if digits[1][-1] == 'K':
                result = int(digits[0])*1000 + int(digits[1][:-1])*100
            elif digits[1][-1] == 'M':
                result = int(digits[0])*1000000 + int(digits[1][:-1])*100000
        elif len(digits) == 1:
            if digits[0][-1] == 'K':
                result = int(digits[0][:-1])*1000
            elif digits[0][-1] == 'M':
                result = int(digits[0][:-1])*1000000
            else:
                result = int(digits[0])
    except Exception as e:
        print(e)
        result = None

    return(result)


def fetch_share_count(page_url, detailed=False):
    """
    Function fetching the (approximate) number of Facebook shares for the given url.

    Args:
        page_url (str): Target URL as a string.

    Returns:
        dict: The HTML of the page.
    """
    page_url = strip_protocol(page_url)
    user_agent = {
        'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0'}
    pool = urllib3.PoolManager(headers=user_agent)
    try:
        http_button_request = "https://www.facebook.com/plugins/like.php?href=" + \
            quote("http://" + page_url) + "&layout=box_count"
        https_button_request = "https://www.facebook.com/plugins/like.php?href=" + \
            quote("https://" + page_url) + "&layout=box_count"
        http_button_html = pool.request(
            'GET', http_button_request).data.decode('utf-8')
        http_button_soup = BeautifulSoup(http_button_html, 'html.parser')
        http_button_result = http_button_soup.find(
            'span', attrs={"id": u"u_0_0"}).get_text()

        https_button_html = pool.request(
            'GET', https_button_request).data.decode('utf-8')
        https_button_soup = BeautifulSoup(https_button_html, 'html.parser')
        https_button_result = https_button_soup.find(
            'span', attrs={"id": u"u_0_0"}).get_text()
    except Exception as e:
        print(e)
        http_button_result = None
        https_button_result = None
    http_button_result = format_button_result(http_button_result)
    https_button_result = format_button_result(https_button_result)
    if detailed:
        return {"http": http_button_result, "https": https_button_result}
    else:
        # Seemingly working heuristic
        return max(http_button_result, https_button_result)


def fetch_share_counts(urls):
    for url in urls:
        yield fetch_share_count(url)
