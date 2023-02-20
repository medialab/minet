# =============================================================================
# Minet CrowdTangle Links Summary CLI Action
# =============================================================================
#
# Logic of the `ct summary` action.
#
import casanova

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.crowdtangle.utils import with_crowdtangle_utilities
from minet.crowdtangle.constants import (
    CROWDTANGLE_SUMMARY_CSV_HEADERS,
    CROWDTANGLE_POST_CSV_HEADERS_WITH_LINK,
)

# TODO: could be a nested loading bar


@with_crowdtangle_utilities
@with_enricher_and_loading_bar(
    headers=CROWDTANGLE_SUMMARY_CSV_HEADERS, title="Collecting data", unit="urls"
)
def action(cli_args, client, enricher, loading_bar):
    posts_writer = None

    if cli_args.posts is not None:
        posts_writer = casanova.writer(
            cli_args.posts, fieldnames=CROWDTANGLE_POST_CSV_HEADERS_WITH_LINK
        )

    for row, url in enricher.cells(cli_args.column, with_rows=True):
        url = url.strip()

        stats = client.summary(
            url,
            start_date=cli_args.start_date,
            with_top_posts=cli_args.posts is not None,
            sort_by=cli_args.sort_by,
            platforms=cli_args.platforms,
        )

        if cli_args.posts is not None:
            stats, posts = stats

            if posts is not None:
                for post in posts:
                    posts_writer.writerow(post.as_csv_row())

        enricher.writerow(row, stats.as_csv_row() if stats is not None else None)

        loading_bar.advance()
