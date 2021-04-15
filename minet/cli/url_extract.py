# =============================================================================
# Minet Url Extract CLI Action
# =============================================================================
#
# Logic of the `url-extract` action.
#
import casanova
from ural import urls_from_text, urls_from_html
from urllib.parse import urljoin

from minet.cli.utils import LoadingBar

REPORT_HEADERS = [
    'extracted_url'
]

EXTRACTORS = {
    'html': urls_from_html,
    'text': urls_from_text
}


def url_extract_action(cli_args):
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=REPORT_HEADERS,
        keep=cli_args.select
    )

    extract = EXTRACTORS[getattr(cli_args, 'from')]

    loading_bar = LoadingBar(
        desc='Extracting',
        unit='row',
        total=cli_args.total
    )

    for row, content in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.update()

        content = content.strip()

        if not content:
            continue

        for url in extract(content):
            if cli_args.base_url is not None:
                url = urljoin(cli_args.base_url, url)

            enricher.writerow(row, [url])
