# =============================================================================
# Minet Reddit Posts CLI Action
# =============================================================================
#
# Logic of the `rd posts` action.
#
from minet.cli.utils import with_enricher_and_loading_bar

from minet.reddit.scraper import RedditScraper
from minet.reddit.types import RedditPost
from minet.reddit.exceptions import RedditInvalidTargetError


@with_enricher_and_loading_bar(
    headers=RedditPost,
    title="Scraping posts",
    unit="pages",
    nested=True,
    sub_unit="posts",
)
def action(cli_args, enricher, loading_bar):
    scraper = RedditScraper()

    for i, row, url in enricher.enumerate_cells(
        cli_args.column, with_rows=True, start=1
    ):
        with loading_bar.step(url):
            try:
                posts = scraper.get_posts(
                    url, "subreddit", cli_args.text, cli_args.limit
                )

            except RedditInvalidTargetError:
                loading_bar.print(
                    "the script could not complete normally on line %i" % (i)
                )
                continue

            for post in posts:
                loading_bar.nested_advance()
                enricher.writerow(row, post)
