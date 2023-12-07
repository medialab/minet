from minet.cli.utils import with_enricher_and_loading_bar
from minet.youtube.scraper import YouTubeScraper


@with_enricher_and_loading_bar(
    headers=["url"],
    title="Retrieving channel links",
    unit="channels",
    sub_unit="links",
    nested=True,
)
def action(cli_args, enricher, loading_bar):
    scraper = YouTubeScraper()

    for row, channel_url in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(channel_url):
            links = scraper.get_channel_links(channel_url)

            if links is None:
                continue

            for link in links:
                enricher.writerow(row, [link])
