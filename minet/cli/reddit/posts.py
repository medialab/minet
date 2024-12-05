# =============================================================================
# Minet Reddit Posts CLI Action
# =============================================================================
#
# Logic of the `rd posts` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.reddit.scraper import RedditScraper
from minet.reddit.types import RedditPost



@with_enricher_and_loading_bar(
    headers={"post_url"},
    title="Scraping posts",
    unit="groups",
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
                if cli_args.number:
                    posts = scraper.get_posts_urls(url, cli_args.number)
                else:
                    posts = scraper.get_posts_urls(url)
            except :
                loading_bar.print(
                    "problème"
                )
                continue
        
            list_posts = []
            for post in posts:
                list_posts.append({post})
            
            for post in list_posts:
                loading_bar.nested_advance()
                enricher.writerow(row, post)
