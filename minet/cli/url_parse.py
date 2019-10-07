# =============================================================================
# Minet Url Parse CLI Action
# =============================================================================
#
# Logic of the `url-parse` action.
#
import csv
from ural import is_url, normalize_url, get_domain_name
from tqdm import tqdm

from minet.cli.utils import custom_reader, DummyTqdmFile

REPORT_HEADERS = ['normalized_url', 'domain_name']
EMPTY = [''] * len(REPORT_HEADERS)


def url_parse_action(namespace):

    headers, pos, reader = custom_reader(namespace.file, namespace.column)

    if namespace.select:
        selected_headers = namespace.select.split(',')
        selected_pos = [headers.index(h) for h in selected_headers]
        headers = selected_headers

    if namespace.output is None:
        output_file = DummyTqdmFile()
    else:
        output_file = open(namespace.output, 'w')

    writer = csv.writer(output_file)
    writer.writerow(headers + REPORT_HEADERS)

    loading_bar = tqdm(
        desc='Reporting',
        dynamic_ncols=True,
        unit=' lines',
        total=namespace.total
    )

    for line in reader:
        url_data = line[pos].strip()

        loading_bar.update()

        if namespace.select:
            line = [line[p] for p in selected_pos]

        if namespace.separator:
            urls = url_data.split(namespace.separator)
        else:
            urls = [url_data]

        for url in urls:
            if not is_url(url, allow_spaces_in_path=True):
                writer.writerow(line + EMPTY)
                continue

            normalized = normalize_url(url, strip_trailing_slash=True)
            domain = get_domain_name(url)

            line.extend([normalized, domain])

            writer.writerow(line)

    output_file.close()
