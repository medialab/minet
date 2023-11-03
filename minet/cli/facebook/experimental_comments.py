from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.facebook.emulated_scraper import FacebookEmulatedScraper
from minet.facebook.exceptions import FacebookInvalidTargetError
from minet.facebook.types import FacebookComment


@with_enricher_and_loading_bar(
    headers=FacebookComment,
    title="Scraping comments",
    unit="posts",
    nested=True,
    sub_unit="comments",
)
def action(cli_args, enricher, loading_bar: LoadingBar):
    with FacebookEmulatedScraper(headless=not cli_args.headful) as scraper:
        for i, row, url in enricher.enumerate_cells(
            cli_args.column, with_rows=True, start=1
        ):
            with loading_bar.step(url):
                try:
                    comments = scraper.scrape_comments(url)
                except FacebookInvalidTargetError:
                    loading_bar.print(
                        "Given url (line %i) is probably not a Facebook group post: %s"
                        % (i, url)
                    )
                    continue

                for comment in comments:
                    enricher.writerow(row, comment)

                loading_bar.nested_advance(len(comments))
