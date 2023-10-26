# =============================================================================
# Minet Instagram Comments CLI Action
# =============================================================================
#
# Logic of the `instagram comments` action.
#
from itertools import islice

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.instagram.utils import with_instagram_fatal_errors
from minet.instagram import InstagramAPIScraper
from minet.instagram.constants import INSTAGRAM_COMMENT_CSV_HEADERS
from minet.instagram.exceptions import InstagramInvalidTargetError


@with_instagram_fatal_errors
@with_enricher_and_loading_bar(
    headers=INSTAGRAM_COMMENT_CSV_HEADERS,
    title="Scraping post comments",
    unit="posts",
    nested=True,
    sub_unit="comments",
)
def action(cli_args, enricher, loading_bar):
    client = InstagramAPIScraper(cookie=cli_args.cookie)

    for i, row, post in enricher.enumerate_cells(
        cli_args.column, with_rows=True, start=1
    ):
        with loading_bar.step(post):
            try:
                generator = client.comments(post)

                if cli_args.limit:
                    generator = islice(generator, cli_args.limit)

                for comment in generator:
                    enricher.writerow(row, comment)
                    loading_bar.nested_advance()

            except InstagramInvalidTargetError:
                loading_bar.print(
                    "Given post (line %i) is probably not an Instagram post: %s"
                    % (i, post)
                )
