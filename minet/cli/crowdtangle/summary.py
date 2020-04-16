# =============================================================================
# Minet CrowdTangle Links Summary CLI Action
# =============================================================================
#
# Logic of the `ct summary` action.
#
import csv
from io import StringIO
from tqdm import tqdm
from ural import is_url

from minet.cli.utils import die, custom_reader
from minet.crowdtangle.constants import (
    CROWDTANGLE_SUMMARY_CSV_HEADERS,
    CROWDTANGLE_POST_CSV_HEADERS_WITH_LINK
)
from minet.crowdtangle.exceptions import (
    CrowdTangleInvalidTokenError
)
from minet.crowdtangle.summary import crowdtangle_summary

CSV_PADDING = ['0'] * len(CROWDTANGLE_SUMMARY_CSV_HEADERS)


def forge_url_from_namespace(namespace, link):
    return forge_url(
        link=link,
        token=namespace.token,
        start_date=namespace.start_date,
        sort_by=namespace.sort_by,
        include_posts=namespace.posts is not None
    )


def crowdtangle_summary_action(namespace, output_file):
    if not namespace.start_date:
        die('Missing --start-date!')

    if is_url(namespace.column):
        namespace.file = StringIO('url\n%s' % namespace.column)
        namespace.column = 'url'

    input_headers, pos, reader = custom_reader(namespace.file, namespace.column)

    output_headers = input_headers + CROWDTANGLE_SUMMARY_CSV_HEADERS
    output_writer = csv.writer(output_file)
    output_writer.writerow(output_headers)

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

    def key(line):
        return line[pos]

    iterator = crowdtangle_summary(
        reader,
        key=key,
        token=namespace.token,
        start_date=namespace.start_date,
        with_top_posts=namespace.posts is not None,
        rate_limit=namespace.rate_limit,
        sort_by=namespace.sort_by,
        format='csv_row'
    )

    try:
        for result in iterator:
            line = result.item

            if result.stats is None:
                output_writer.writerow(line + CSV_PADDING)
            else:
                output_writer.writerow(line + result.stats)

            if namespace.posts is not None and result.posts is not None:
                for post in result.posts:
                    posts_writer.writerow(post)

            loading_bar.update()

    except CrowdTangleInvalidTokenError:
        die([
            'Your API token is invalid.',
            'Check that you indicated a valid one using the `--token` argument.'
        ])

    except Exception as err:
        raise err
