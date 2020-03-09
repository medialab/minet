# =============================================================================
# Minet Url Extract CLI Action
# =============================================================================
#
# Logic of the `url-extract` action.
#
from tqdm import tqdm
from ural import urls_from_text, urls_from_html
from urllib.parse import urljoin

from minet.cli.utils import CSVEnricher, open_output_file

REPORT_HEADERS = [
    'url'
]

EXTRACTORS = {
    'html': urls_from_html,
    'text': urls_from_text
}


def url_extract_action(namespace):
    output_file = open_output_file(namespace.output)

    enricher = CSVEnricher(
        namespace.file,
        namespace.column,
        output_file,
        report_headers=REPORT_HEADERS,
        select=namespace.select.split(',') if namespace.select else None
    )

    extract = EXTRACTORS[getattr(namespace, 'from')]

    loading_bar = tqdm(
        desc='Reading',
        dynamic_ncols=True,
        unit=' lines',
        total=namespace.total
    )

    for line in enricher:
        loading_bar.update()

        content = line[enricher.pos].strip()

        if not content:
            continue

        for url in extract(content):
            if namespace.base_url is not None:
                url = urljoin(namespace.base_url, url)

            enricher.write(line, [url])

    output_file.close()
