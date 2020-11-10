# =============================================================================
# Minet CrowdTangle Links Summary CLI Action
# =============================================================================
#
# Logic of the `ct summary` action.
#
import csv
import casanova
from io import StringIO
from tqdm import tqdm
from ural import is_url

from minet.cli.utils import die
from minet.crowdtangle.constants import (
    CROWDTANGLE_SUMMARY_CSV_HEADERS,
    CROWDTANGLE_POST_CSV_HEADERS_WITH_LINK
)
from minet.crowdtangle.exceptions import (
    CrowdTangleInvalidTokenError
)
from minet.crowdtangle import CrowdTangleClient


def crowdtangle_summary_action(namespace, output_file):
    if not namespace.start_date:
        die('Missing --start-date!')

    if is_url(namespace.column):
        namespace.file = StringIO('url\n%s' % namespace.column)
        namespace.column = 'url'

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        keep=namespace.select.split(',') if namespace.select else None,
        add=CROWDTANGLE_SUMMARY_CSV_HEADERS
    )

    posts_writer = None

    if namespace.posts is not None:
        posts_writer = csv.writer(namespace.posts)
        posts_writer.writerow(CROWDTANGLE_POST_CSV_HEADERS_WITH_LINK)

    loading_bar = tqdm(
        desc='Collecting data',
        dynamic_ncols=True,
        total=namespace.total,
        unit=' urls'
    )

    client = CrowdTangleClient(namespace.token, rate_limit=namespace.rate_limit)

    for row, url in enricher.cells(namespace.column, with_rows=True):
        url = url.strip()

        try:
            stats = client.summary(
                url,
                start_date=namespace.start_date,
                with_top_posts=namespace.posts is not None,
                sort_by=namespace.sort_by,
                format='csv_row',
                platforms=namespace.platforms
            )

        except CrowdTangleInvalidTokenError:
            die([
                'Your API token is invalid.',
                'Check that you indicated a valid one using the `--token` argument.'
            ])

        except Exception as err:
            raise err

        if namespace.posts is not None:
            stats, posts = stats

            if posts is not None:
                for post in posts:
                    posts_writer.writerow([url] + post)

        enricher.writerow(row, stats)

        loading_bar.update()
