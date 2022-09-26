# =============================================================================
# Minet Instagram Hashtag CLI Action
# =============================================================================
#
# Logic of the `instagram hashtag` action.
#
import casanova
from itertools import islice

from minet.cli.utils import LoadingBar
from minet.instagram import InstagramAPIScraper
from minet.instagram.constants import INSTAGRAM_POST_CSV_HEADERS


def hashtag_action(cli_args):
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=INSTAGRAM_POST_CSV_HEADERS,
    )

    loading_bar = LoadingBar("Retrieving posts", unit="post", stats={"posts": 0})

    client = InstagramAPIScraper(cookie=cli_args.cookie)
    for row, hashtag in enricher.cells(cli_args.column, with_rows=True):
        generator = client.search_hashtag(hashtag)

        if cli_args.limit:
            generator = islice(generator, cli_args.limit)

        for hashtag in generator:
            loading_bar.update()
            enricher.writerow(row, hashtag.as_csv_row())

            loading_bar.inc("posts")
