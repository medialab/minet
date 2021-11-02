# =============================================================================
# Minet BuzzSumo Domain CLI Action
# =============================================================================
#
# Logic of the `bz domain` action.
#

import casanova

from minet.cli.utils import LoadingBar
from minet.buzzsumo.utils import (
    convert_string_date_into_timestamp,
    construct_url,
    URL_TEMPLATE,
    call_buzzsumo_once
)


ARTICLES_HEADERS = [
    'id',
    'published_date',
    'updated_at',
    'url',
    'og_url',
    'thumbnail',
    'domain_name',
    'subdomain',
    'num_linking_domains',
    'total_shares',
    'total_facebook_shares',
    'facebook_comments',
    'facebook_shares',
    'facebook_likes',
    'love_count',
    'wow_count',
    'haha_count',
    'angry_count',
    'sad_count',
    'twitter_shares',
    'twitter_user_id',
    'pinterest_shares',
    'total_reddit_engagements',
    'alexa_rank',
    'evergreen_score',
    'evergreen_score2',
    'youtube_trending_score',
    'youtube_views',
    'youtube_likes',
    'youtube_dislikes',
    'youtube_comments',
    'article_amplifiers',
    'title',
    'display_title',
    'author_name',
    'language',
    'num_words',
    'article_types',
    'video_length',
]


def get_nb_pages_per_period_dates(period_dates, domain_base_url):

    nb_pages = []

    for period_dates_index in range(len(period_dates) - 1):

        url = domain_base_url + '&begin_date=%s' % period_dates[period_dates_index]
        url += '&end_date=%s' % (period_dates[period_dates_index + 1] - 1)

        data, _ = call_buzzsumo_once(url)
        nb_pages.append(data['total_pages'])

    return nb_pages


def optimize_period_dates_wrt_nb_pages(period_dates, nb_pages, maximum_page_nb):

    new_period_dates = period_dates

    if any(nb_page > maximum_page_nb for nb_page in nb_pages):
        for nb_page_index in range(len(nb_pages)):
            if nb_pages[nb_page_index] > maximum_page_nb:
                new_period_dates.append((period_dates[nb_page_index] + period_dates[nb_page_index + 1]) / 2)

        new_period_dates.sort()

    return new_period_dates


def buzzsumo_domain_action(cli_args):

    base_url = construct_url(URL_TEMPLATE, cli_args.token)

    begin_date = convert_string_date_into_timestamp(cli_args.begin_date)
    end_date = convert_string_date_into_timestamp(cli_args.end_date)

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=ARTICLES_HEADERS,
    )

    loading_bar = LoadingBar(
        desc='Retrieving domain articles',
        unit='domain',
        total=enricher.total
    )

    for row, domain_name in enricher.cells(cli_args.column, with_rows=True):

        domain_base_url = base_url + '&q=%s' % domain_name

        # Here we optimize the periods used to request the API, because BuzzSumo
        # prevents us from getting more than 99 pages.
        maximum_page_nb = 98
        period_dates = [begin_date, end_date]
        nb_pages = [1000]

        # This loop creates adapted time periods that all return less than 99 pages of results:
        while any(nb_page > maximum_page_nb for nb_page in nb_pages):

            # We ask how many pages are needed to get all the articles for the given periods:
            nb_pages = get_nb_pages_per_period_dates(period_dates, domain_base_url)

            # If a given period gets more than 98 pages, this period is then cut down in half:
            period_dates = optimize_period_dates_wrt_nb_pages(period_dates, nb_pages, maximum_page_nb)

        # Now we get all the results for the optimized periods
        for period_dates_index in range(len(period_dates) - 1):

            url = domain_base_url + '&begin_date=%s' % period_dates[period_dates_index]
            url += '&end_date=%s' % (period_dates[period_dates_index + 1] - 1)
            page = 0

            while True:

                data, _ = call_buzzsumo_once(url + '&page=%s' % page)

                if data['results'] == []:
                    break
                else:
                    for result in data['results']:
                        enricher.writerow(row, [result[column_name] for column_name in ARTICLES_HEADERS])
                    page += 1

        loading_bar.update()
