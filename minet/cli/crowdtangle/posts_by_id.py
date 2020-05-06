# =============================================================================
# Minet CrowdTangle Posts By Id CLI Action
# =============================================================================
#
# Logic of the `ct posts-by-id` action.
#
import re
import casanova
from tqdm import tqdm
from ural import ensure_protocol
from ural.facebook import (
    is_facebook_url,
    parse_facebook_url,
    FacebookPost
)

from minet.cli.utils import die
from minet.crowdtangle.constants import CROWDTANGLE_POST_CSV_HEADERS
from minet.crowdtangle.client import CrowdTangleClient
from minet.crowdtangle.exceptions import CrowdTangleInvalidTokenError

ID_PATTERN = re.compile(r'^\d{8,}$')


def is_post_id(value):
    return bool(re.search(ID_PATTERN, value))


def extract_facebook_post_id(value):
    value = value.strip()

    if not value:
        return None

    if is_post_id(value):
        return value

    value = ensure_protocol(value)

    if is_facebook_url(value):
        parsed = parse_facebook_url(value)

        if isinstance(parsed, FacebookPost):
            return parsed.id

    return None


def crowdtangle_posts_by_id_action(namespace, output_file):

    client = CrowdTangleClient(namespace.token, rate_limit=namespace.rate_limit)

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        keep=namespace.select,
        add=CROWDTANGLE_POST_CSV_HEADERS
    )

    loading_bar = tqdm(
        desc='Retrieving posts',
        dynamic_ncols=True,
        total=namespace.total,
        unit=' posts'
    )

    try:
        for row, post_id in enricher.cells(namespace.column, with_rows=True):
            loading_bar.update()

            post_id = extract_facebook_post_id(post_id)

            if post_id is None:
                enricher.writerow(row)
                continue

            post = client.post(post_id, format='csv_row')

            print(post)
            break

    except CrowdTangleInvalidTokenError:
        die([
            'Your API token is invalid.',
            'Check that you indicated a valid one using the `--token` argument.'
        ])
