# =============================================================================
# Minet Tiktok Scrape Commercials CLI Action
# =============================================================================
#
# Logic of the `tiktok scrape-commercials` action.
#
from itertools import islice
import casanova

from minet.cli.utils import with_loading_bar
from minet.tiktok import TiktokAPIScraper
from minet.tiktok.types import TiktokCommercialContent


@with_loading_bar(
    title="Searching commercials",
    unit="commercials",
    nested=False,
)
def action(cli_args, loading_bar):
    client = TiktokAPIScraper()
    generator = client.search_commercial_contents(
        country=cli_args.country, min_date=cli_args.min_date, max_date=cli_args.max_date
    )

    writer = casanova.writer(cli_args.output, fieldnames=TiktokCommercialContent)

    if cli_args.total:
        generator = islice(generator, cli_args.total)

    for video in generator:
        with loading_bar.step(video):
            writer.writerow(video.as_csv_row())
