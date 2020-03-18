# =============================================================================
# Minet Facebook Url Parse CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and parsing the Facebook urls
# contained in a given column.
#
from tqdm import tqdm
from ural.facebook import (
    parse_facebook_url,
    FacebookPost,
    FacebookUser,
    FacebookHandle
)

from minet.cli.utils import CSVEnricher, open_output_file

REPORT_HEADERS = ['facebook_type', 'facebook_id', 'facebook_handle', 'facebook_normalized_url']


def facebook_url_parse_action(namespace):
    output_file = open_output_file(namespace.output)

    enricher = CSVEnricher(
        namespace.file,
        namespace.column,
        output_file,
        report_headers=REPORT_HEADERS,
        select=namespace.select.split(',') if namespace.select else None
    )

    loading_bar = tqdm(
        desc='Parsing',
        dynamic_ncols=True,
        unit=' lines',
    )

    for line in enricher:

        loading_bar.update()

        url_data = line[enricher.pos].strip()

        parsed = parse_facebook_url(url_data)

        if parsed is None:
            enricher.write_empty(line)

        if isinstance(parsed, FacebookPost):
            enricher.write(
                line,
                ['post', parsed.id, '', parsed.url]
            )

        elif isinstance(parsed, FacebookHandle):
            enricher.write(
                line,
                ['handle', '', parsed.handle, parsed.url]
            )

        elif isinstance(parsed, FacebookUser):
            enricher.write(
                line,
                ['user', parsed.id or '', parsed.handle or '', parsed.url]
            )
