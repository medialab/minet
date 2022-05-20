# =============================================================================
# Minet Twitter Scrape CLI Action
# =============================================================================
#
# Logic of the `tw scrape` action.
#
import casanova
from twitwi.constants import TWEET_FIELDS, USER_FIELDS
from twitwi import format_tweet_as_csv_row, format_user_as_csv_row

from minet.utils import PseudoFStringFormatter
from minet.cli.utils import LoadingBar
from minet.twitter import TwitterAPIScraper
from minet.twitter.exceptions import TwitterPublicAPIOverCapacityError
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


def twitter_scrape_action(cli_args):
    scraper = TwitterAPIScraper()

    unit = cli_args.items[:-1]

    # Stats
    loading_bar = LoadingBar(
        "Collecting %s" % unit,
        total=cli_args.limit,
        unit=unit,
        stats={"queries": 0},
    )

    headers = (
        (TWEET_FIELDS + ADDITIONAL_TWEET_FIELDS)
        if cli_args.items == "tweets"
        else USER_FIELDS
    )

    enricher = casanova.enricher(
        cli_args.file, cli_args.output, add=headers, keep=cli_args.select
    )

    for row, query in enricher.cells(cli_args.query, with_rows=True):

        # Templating?
        if cli_args.query_template is not None:
            query = CUSTOM_FORMATTER.format(cli_args.query_template, value=query)

        loading_bar.print('Searching for "%s"' % query)
        loading_bar.inc("queries")

        if cli_args.items == "tweets":
            iterator = scraper.search_tweets(
                query,
                limit=cli_args.limit,
                include_referenced_tweets=cli_args.include_refs,
                with_meta=True,
            )
        else:
            iterator = scraper.search_users(query, limit=cli_args.limit)

        try:
            for data in iterator:
                loading_bar.update()

                if cli_args.items == "tweets":
                    tweet, meta = data
                    tweet_row = format_tweet_as_csv_row(tweet)
                    addendum = tweet_row + format_meta_row(meta)
                else:
                    addendum = format_user_as_csv_row(data)

                enricher.writerow(row, addendum)

        except TwitterPublicAPIOverCapacityError:
            loading_bar.die('Got an "Over Capacity" error. Shutting down...')
