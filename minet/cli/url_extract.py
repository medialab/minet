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


def url_extract_action(namespace):
    output_file = open_output_file(namespace.output)

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        add=REPORT_HEADERS,
        keep=namespace.select.split(',') if namespace.select else None
    )

    extract = EXTRACTORS[getattr(namespace, 'from')]

    loading_bar = tqdm(
        desc='Extracting',
        dynamic_ncols=True,
        unit=' rows',
        total=namespace.total
    )

    for row, content in enricher.cells(namespace.column, with_rows=True):
        loading_bar.update()

        content = content.strip()

        if not content:
            continue

        for url in extract(content):
            if namespace.base_url is not None:
                url = urljoin(namespace.base_url, url)

            enricher.writerow(row, [url])

    output_file.close()
