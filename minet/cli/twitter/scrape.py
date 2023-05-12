# =============================================================================
# Minet Twitter Scrape CLI Action
# =============================================================================
#
# Logic of the `tw scrape` action.
#
from twitwi.constants import TWEET_FIELDS, USER_FIELDS
from twitwi import format_tweet_as_csv_row, format_user_as_csv_row

from minet.utils import PseudoFStringFormatter
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.exceptions import FatalError
from minet.twitter import TwitterAPIScraper
from minet.twitter.exceptions import (
    TwitterPublicAPIQueryTooLongError,
    TwitterPublicAPIInvalidCookieError,
    TwitterPublicAPIBadAuthError,
)
from minet.twitter.constants import ADDITIONAL_TWEET_FIELDS

CUSTOM_FORMATTER = PseudoFStringFormatter()


def format_meta_row(meta):
    if meta is None:
        return [""] * len(ADDITIONAL_TWEET_FIELDS)

    return [
        meta.get("intervention_type"),
        meta.get("intervention_text"),
        meta.get("intervention_url"),
    ]


def get_headers(cli_args):
    return (
        (TWEET_FIELDS + ADDITIONAL_TWEET_FIELDS)
        if cli_args.items == "tweets"
        else USER_FIELDS
    )


@with_enricher_and_loading_bar(
    headers=get_headers,
    title="Scraping",
    unit="queries",
    nested=True,
    sub_unit=lambda cli_args: cli_args.items,
)
def action(cli_args, enricher, loading_bar):
    try:
        scraper = TwitterAPIScraper(cli_args.cookie)
    except TwitterPublicAPIInvalidCookieError:
        raise FatalError(
            [
                "Invalid Twitter cookie!",
                "Try giving another browser to --cookie and sure you are correctly logged in.",
            ]
        )

    for row, query in enricher.cells(cli_args.column, with_rows=True):
        # Templating?
        if cli_args.query_template is not None:
            query = CUSTOM_FORMATTER.format(cli_args.query_template, value=query)

        with loading_bar.step(query):
            if cli_args.items == "tweets":
                iterator = scraper.search_tweets(
                    query,
                    locale=cli_args.timezone,
                    limit=cli_args.limit,
                    include_referenced_tweets=cli_args.include_refs,
                    with_meta=True,
                )
            else:
                iterator = scraper.search_users(
                    query, locale=cli_args.timezone, limit=cli_args.limit
                )

            try:
                for data in iterator:
                    if cli_args.items == "tweets":
                        tweet, meta = data
                        tweet_row = format_tweet_as_csv_row(tweet)
                        addendum = tweet_row + format_meta_row(meta)
                    else:
                        addendum = format_user_as_csv_row(data)

                    enricher.writerow(row, addendum)
                    loading_bar.nested_advance()

            except TwitterPublicAPIQueryTooLongError:
                loading_bar.error("Query too long [dim]%s[/dim]" % query)

            except TwitterPublicAPIBadAuthError as error:
                raise FatalError(
                    "Bad authentication (%i). Double check your --cookie and make sure you are logged in."
                    % error.status
                )
