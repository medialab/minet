# =============================================================================
# Minet BuzzSumo Domain CLI Action
# =============================================================================
#
# Logic of the `bz domain` action.
#

import csv
import casanova

from minet.cli.utils import LoadingBar
from minet.cli.buzzsumo.domain_summary import (convert_date_to_correct_format, call_buzzsumo_once)
# from minet.web import request_json


URL_TEMPLATE = 'https://api.buzzsumo.com/search/articles.json?api_key=%s'

ARTICLES_HEADERS = [
    'id',
    'url',
    'title',
    'published_date',
    'updated_at',
    'domain_name',
    'total_shares',
    'total_facebook_shares',
    'facebook_likes',
    'facebook_comments',
    'facebook_shares',
    'twitter_shares',
    'pinterest_shares',
    'total_reddit_engagements',
    'alexa_rank',
]


def get_nb_pages_per_period_dates(period_dates, domain_base_url):

    nb_pages = []

    for period_dates_index in range(len(period_dates) - 1):

        url = domain_base_url + '&begin_date=%s' % period_dates[period_dates_index]
        url += '&end_date=%s' % (period_dates[period_dates_index + 1] - 1)

        response = call_buzzsumo_once(url)
        nb_pages.append(response['total_pages'])

    return nb_pages


def optimize_period_dates_wrt_nb_pages(period_dates, nb_pages):

    new_period_dates = period_dates

    if any(nb_page > 99 for nb_page in nb_pages):
        for nb_page_index in range(len(nb_pages)):
            if nb_pages[nb_page_index] > 99:
                new_period_dates.append((period_dates[nb_page_index] + period_dates[nb_page_index + 1]) / 2)

        new_period_dates.sort()

    return new_period_dates


def construct_url(url, token):
    url = url % token
    url += '&num_results=100'
    return url


def buzzsumo_domain_action(cli_args):

    articles_writer = csv.writer(cli_args.articles)
    articles_writer.writerow(ARTICLES_HEADERS)

    base_url = construct_url(URL_TEMPLATE, cli_args.token)

    begin_date, end_date = convert_date_to_correct_format(cli_args.begin_date, cli_args.end_date)

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=[],
    )

    loading_bar = LoadingBar(
        desc='Retrieving domain',
        unit='domain',
        total=enricher.total
    )

    for row, domain_name in enricher.cells(cli_args.column, with_rows=True):

        domain_base_url = base_url + '&q=%s' % domain_name

        # Here we optimize the periods used to create the API requests, because Buzzsumo
        # prevents us from getting more than 100 pages for one request, thus we create
        # adapted time periods that return less than 100 pages.
        period_dates = [begin_date, end_date]
        nb_pages = [1000]
        while any(nb_page > 99 for nb_page in nb_pages):
            nb_pages = get_nb_pages_per_period_dates(period_dates, domain_base_url)
            period_dates = optimize_period_dates_wrt_nb_pages(period_dates, nb_pages)

        # Now we get all the results for the optimized periods
        for period_dates_index in range(len(period_dates) - 1):

            url = domain_base_url + '&begin_date=%s' % period_dates[period_dates_index]
            url += '&end_date=%s' % (period_dates[period_dates_index + 1] - 1)
            page = 0

            while True:

                response = call_buzzsumo_once(url + '&page=%s' % page)

                if response['results'] == []:
                    break
                else:
                    for result in response['results']:
                        articles_writer.writerow([result[column_name] for column_name in ARTICLES_HEADERS])
                    page += 1

        loading_bar.update()
        enricher.writerow(row)
