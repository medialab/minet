# =============================================================================
# Minet Url Extract CLI Action
# =============================================================================
#
# Logic of the `url-extract` action.
#
import casanova
from tqdm import tqdm
from ural import urls_from_text, urls_from_html
from urllib.parse import urljoin

from minet.cli.utils import open_output_file

REPORT_HEADERS = [
    'url'
]

EXTRACTORS = {
    'html': urls_from_html,
    'text': urls_from_text
}


def url_extract_action(cli_args):
    output_file = open_output_file(cli_args.output)

    enricher = casanova.enricher(
        cli_args.file,
        output_file,
        add=REPORT_HEADERS,
        keep=cli_args.select.split(',') if cli_args.select else None
    )

    extract = EXTRACTORS[getattr(cli_args, 'from')]

    loading_bar = tqdm(
        desc='Extracting',
        dynamic_ncols=True,
        unit=' rows',
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

    output_file.close()
