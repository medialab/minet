# =============================================================================
# Minet CrowdTangle Links Summary CLI Action
# =============================================================================
#
# Logic of the `ct summary` action.
#
import csv
import casanova
from tqdm import tqdm
from ural import is_url

from minet.cli.utils import die, edit_cli_args_with_csv_io
from minet.crowdtangle.constants import (
    CROWDTANGLE_SUMMARY_CSV_HEADERS,
    CROWDTANGLE_POST_CSV_HEADERS_WITH_LINK
)
from minet.crowdtangle.exceptions import (
    CrowdTangleInvalidTokenError
)
from minet.crowdtangle import CrowdTangleAPIClient


def crowdtangle_summary_action(cli_args, output_file):
    if not cli_args.start_date:
        die('Missing --start-date!')

    if is_url(cli_args.column):
        edit_cli_args_with_csv_io(cli_args, 'url')

    enricher = casanova.enricher(
        cli_args.file,
        output_file,
        keep=cli_args.select.split(',') if cli_args.select else None,
        add=CROWDTANGLE_SUMMARY_CSV_HEADERS
    )

    posts_writer = None

    if cli_args.posts is not None:
        posts_writer = csv.writer(cli_args.posts)
        posts_writer.writerow(CROWDTANGLE_POST_CSV_HEADERS_WITH_LINK)

    loading_bar = tqdm(
        desc='Collecting data',
        dynamic_ncols=True,
        total=cli_args.total,
        unit=' urls'
    )

    client = CrowdTangleAPIClient(cli_args.token, rate_limit=cli_args.rate_limit)

    for row, url in enricher.cells(cli_args.column, with_rows=True):
        url = url.strip()

        try:
            stats = client.summary(
                url,
                start_date=cli_args.start_date,
                with_top_posts=cli_args.posts is not None,
                sort_by=cli_args.sort_by,
                format='csv_row',
                platforms=cli_args.platforms
            )

        except CrowdTangleInvalidTokenError:
            die([
                'Your API token is invalid.',
                'Check that you indicated a valid one using the `--token` argument.'
            ])

        except Exception as err:
            raise err

        if cli_args.posts is not None:
            stats, posts = stats

            if posts is not None:
                for post in posts:
                    posts_writer.writerow([url] + post)

        enricher.writerow(row, stats)

        loading_bar.update()
