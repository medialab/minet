# =============================================================================
# Minet BuzzSumo Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the BuzzSumo namespace.
#
from datetime import datetime
import time

from termcolor import colored

from minet.web import request_json


URL_TEMPLATE = 'https://api.buzzsumo.com/search/articles.json?api_key=%s'


def convert_string_date_into_timestamp(date):
    return datetime.strptime(date, '%Y-%m-%d').timestamp()


def construct_url(url, token, begin_date=None, end_date=None):

    url = url % token

    url += '&num_results=100'

    if begin_date:
        url += '&begin_date=%s' % begin_date
    if end_date:
        url += '&end_date=%s' % (end_date - 1)

    return url


def call_buzzsumo_once(url):

    api_call_attempt = 0

    while True:

        if api_call_attempt == 0:
            start_call_time = time.time()
        # If second try or more, wait an exponential amount of time (first 2 sec, then 4, then 16...)
        else:
            time.sleep(2**(api_call_attempt - 1))

        err, response, data = request_json(url)

        # If first try, add a sleep function so that we wait at least 1.2 seconds between two calls
        if api_call_attempt == 0:
            end_call_time = time.time()
            if (end_call_time - start_call_time) < 1.2:
                time.sleep(1.2 - (end_call_time - start_call_time))

        if err:
            print(colored('Error', 'red'), err)
        else:
            if response.status == 200:
                break
            else:
                print(colored('Error', 'red'), response.status)
                if data:
                    print(data)

    return data, response.headers
