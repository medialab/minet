# =============================================================================
# Minet Instagram Hashtag CLI Action
# =============================================================================
#
# Logic of the `instagram hashtag` action.
#
from itertools import islice

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.instagram.utils import with_instagram_fatal_errors
from minet.instagram import InstagramAPIScraper
from minet.instagram.constants import INSTAGRAM_HASHTAG_POST_CSV_HEADERS
from minet.instagram.exceptions import InstagramHashtagNeverUsedError


@with_instagram_fatal_errors
@with_enricher_and_loading_bar(
    headers=INSTAGRAM_HASHTAG_POST_CSV_HEADERS,
    title="Scraping posts",
    unit="hashtag",
    nested=True,
    sub_unit="posts",
)
def action(cli_args, enricher, loading_bar):
    client = InstagramAPIScraper(cookie=cli_args.cookie)

    for i, row, hashtag in enricher.enumerate_cells(
        cli_args.column, with_rows=True, start=1
    ):
        with loading_bar.step(hashtag):
            try:
                generator = client.search_hashtag(hashtag)

                if cli_args.limit:
                    generator = islice(generator, cli_args.limit)

                for post in generator:
                    enricher.writerow(row, post.as_csv_row())
                    loading_bar.nested_advance()

            except InstagramHashtagNeverUsedError:
                loading_bar.print(
                    "Given hashtag (line %i) has probably never been used: %s"
                    % (i, hashtag)
                )
