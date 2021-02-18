# =============================================================================
# Minet Facebook Url Parse CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and parsing the Facebook urls
# contained in a given column.
#
import casanova
from tqdm import tqdm
from ural.facebook import (
    parse_facebook_url,
    FacebookPost,
    FacebookUser,
    FacebookGroup,
    FacebookHandle,
    FacebookPhoto,
    FacebookVideo
)

from minet.cli.utils import open_output_file

REPORT_HEADERS = [
    'facebook_type',
    'facebook_id',
    'facebook_full_id',
    'facebook_handle',
    'facebook_normalized_url'
]


def facebook_url_parse_action(namespace):
    output_file = open_output_file(namespace.output)

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        keep=namespace.select,
        add=REPORT_HEADERS
    )

    loading_bar = tqdm(
        desc='Parsing',
        dynamic_ncols=True,
        unit=' lines',
    )

    for row, url in enricher.cells(namespace.column, with_rows=True):

        loading_bar.update()

        url_data = url.strip()

        parsed = parse_facebook_url(url_data)

        if parsed is None:
            enricher.writerow(row)

        elif isinstance(parsed, FacebookPost):
            enricher.writerow(
                row,
                ['post', parsed.id, parsed.full_id or '', '', parsed.url]
            )

        elif isinstance(parsed, FacebookHandle):
            enricher.writerow(
                row,
                ['handle', '', '', parsed.handle, parsed.url]
            )

        elif isinstance(parsed, FacebookUser):
            enricher.writerow(
                row,
                ['user', parsed.id or '', '', parsed.handle or '', parsed.url]
            )

        elif isinstance(parsed, FacebookGroup):
            enricher.writerow(
                row,
                ['group', parsed.id or '', '', parsed.handle or '', parsed.url]
            )

        elif isinstance(parsed, FacebookPhoto):
            enricher.writerow(
                row,
                ['photo', parsed.id, '', '', parsed.url]
            )

        elif isinstance(parsed, FacebookVideo):
            enricher.writerow(
                row,
                ['video', parsed.id, '', '', parsed.url]
            )

        else:
            raise TypeError('unknown facebook parse result type!')
