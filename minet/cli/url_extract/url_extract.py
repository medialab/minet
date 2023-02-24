# =============================================================================
# Minet Url Extract CLI Action
# =============================================================================
#
# Logic of the `url-extract` action.
#
from ural import urls_from_text, urls_from_html
from urllib.parse import urljoin

from minet.cli.utils import with_enricher_and_loading_bar

REPORT_HEADERS = ["extracted_url"]

EXTRACTORS = {"html": urls_from_html, "text": urls_from_text}


@with_enricher_and_loading_bar(
    headers=REPORT_HEADERS, title="Extracting urls", unit="docs"
)
def action(cli_args, enricher, loading_bar):
    extract = EXTRACTORS[getattr(cli_args, "from")]

    for row, content in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step():
            content = content.strip()

            if not content:
                continue

            for url in extract(content):
                if cli_args.base_url is not None:
                    url = urljoin(cli_args.base_url, url)

                enricher.writerow(row, [url])
