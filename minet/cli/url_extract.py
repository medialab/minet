# =============================================================================
# Minet Url Extract CLI Action
# =============================================================================
#
# Logic of the `url-extract` action.
#
from tqdm import tqdm

from minet.cli.utils import CSVEnricher, open_output_file

REPORT_HEADERS = [
    'url'
]


def url_extract_action(namespace):
    print(namespace)
    return

    output_file = open_output_file(namespace.output)

    enricher = CSVEnricher(
        namespace.file,
        namespace.column,
        output_file,
        report_headers=REPORT_HEADERS,
        select=namespace.select.split(',') if namespace.select else None
    )

    loading_bar = tqdm(
        desc='Reporting',
        dynamic_ncols=True,
        unit=' lines',
        total=namespace.total
    )

    for line in enricher:
        url_data = line[enricher.pos].strip()

        loading_bar.update()

        if namespace.separator:
            urls = url_data.split(namespace.separator)
        else:
            urls = [url_data]

        for url in urls:
            if not is_url(url, allow_spaces_in_path=True):
                enricher.write_empty(line)
                continue

            normalized = normalize_url(url, strip_trailing_slash=True)

            enricher.write(line, [
                normalize_url(url, strip_trailing_slash=True),
                get_domain_name(url),
                get_hostname(url),
                get_normalized_hostname(url)
            ])

    output_file.close()
