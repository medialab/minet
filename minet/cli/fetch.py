# =============================================================================
# Minet Fetch CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and fetching the urls found
# in the given column. This is done in a respectful multithreaded fashion to
# optimize both running time & memory.
#
import os
import csv
import sys
import gzip
from io import StringIO
from os.path import join, dirname, isfile
from collections import Counter
from tqdm import tqdm
from uuid import uuid4
from ural import is_url

from minet.contiguous_range_set import ContiguousRangeSet

from minet.fetch import multithreaded_fetch
from minet.utils import (
    grab_cookies,
    parse_http_header,
    SliceFormatter
)
from minet.cli.reporters import report_error
from minet.cli.utils import custom_reader, DummyTqdmFile, die

OUTPUT_ADDITIONAL_HEADERS = [
    'line',
    'resolved',
    'status',
    'error',
    'filename',
    'encoding'
]

CUSTOM_FORMATTER = SliceFormatter()


def fetch_action(namespace):

    # Are we resuming
    resuming = namespace.resume

    if resuming and not namespace.output:
        die([
            'Cannot --resume without specifying -o/--output.'
        ])

    # Do we need to fetch only a single url?
    if namespace.file is sys.stdin and is_url(namespace.column):
        namespace.file = StringIO('url\n%s' % namespace.column)
        namespace.column = 'url'

        # If we are hitting a single url we enable contents_in_report
        if namespace.contents_in_report is None:
            namespace.contents_in_report = True

    input_headers, pos, reader = custom_reader(namespace.file, namespace.column)
    filename_pos = input_headers.index(namespace.filename) if namespace.filename else None

    selected_fields = namespace.select.split(',') if namespace.select else None
    selected_pos = [input_headers.index(h) for h in selected_fields] if selected_fields else None

    # HTTP method
    http_method = namespace.method

    # Cookie grabber
    get_cookie = None
    if namespace.grab_cookies:
        get_cookie = grab_cookies(namespace.grab_cookies)

    # Global headers
    global_headers = None
    if namespace.headers:
        global_headers = {}

        for header in namespace.headers:
            k, v = parse_http_header(header)
            global_headers = v

    # Reading output
    output_headers = (list(input_headers) if not selected_pos else [input_headers[i] for i in selected_pos])
    output_headers += OUTPUT_ADDITIONAL_HEADERS

    if namespace.contents_in_report:
        output_headers.append('raw_content')

    if namespace.output is None:
        output_file = DummyTqdmFile(sys.stdout)
    else:
        flag = 'w'

        if resuming and isfile(namespace.output):
            flag = 'r+'

        output_file = open(namespace.output, flag)

    output_writer = csv.writer(output_file)

    if not resuming:
        output_writer.writerow(output_headers)
    else:

        # Reading report to know what need to be done
        _, rpos, resuming_reader = custom_reader(output_file, 'line')

        resuming_reader_loading = tqdm(
            resuming_reader,
            desc='Resuming',
            dynamic_ncols=True,
            unit=' lines'
        )

        already_done = ContiguousRangeSet()

        for line in resuming_reader_loading:
            index = line[rpos]

            already_done.add(int(index))

    # Loading bar
    total = namespace.total

    if total is not None and resuming:
        total -= len(already_done)

    loading_bar = tqdm(
        desc='Fetching pages',
        total=total,
        dynamic_ncols=True,
        unit=' urls'
    )

    def url_key(item):
        line = item[1]
        url = line[pos].strip()

        if not url:
            return

        # Url templating
        if namespace.url_template:
            return namespace.url_template.format(value=url)

        return url

    def request_args(url, item):
        cookie = None

        # Cookie
        if get_cookie:
            cookie = get_cookie(url)

        # Headers
        headers = None

        if global_headers:
            headers = global_headers

        return {
            'method': http_method,
            'cookie': cookie,
            'headers': headers
        }

    def write_output(index, line, resolved=None, status=None, error=None,
                     filename=None, encoding=None, data=None):

        if selected_pos:
            line = [line[p] for p in selected_pos]

        line.extend([
            index,
            resolved or '',
            status or '',
            error or '',
            filename or '',
            encoding or ''
        ])

        if namespace.contents_in_report:
            line.append(data or '')

        output_writer.writerow(line)

    errors = 0
    status_codes = Counter()

    target_iterator = enumerate(reader)

    if resuming:
        target_iterator = (pair for pair in target_iterator if not already_done.stateful_contains(pair[0]))

    multithreaded_iterator = multithreaded_fetch(
        target_iterator,
        key=url_key,
        request_args=request_args,
        threads=namespace.threads,
        throttle=namespace.throttle
    )

    for result in multithreaded_iterator:
        line_index, line = result.item

        if not result.url:

            write_output(
                line_index,
                line
            )

            loading_bar.update()
            continue

        response = result.response
        data = response.data if response is not None else None

        content_write_flag = 'wb'

        # Updating stats
        if result.error is not None:
            errors += 1
        else:
            if response.status >= 400:
                status_codes[response.status] += 1

        postfix = {'errors': errors}

        for code, count in status_codes.most_common(1):
            postfix[str(code)] = count

        loading_bar.set_postfix(**postfix)
        loading_bar.update()

        # No error
        if result.error is None:

            filename = None

            # Building filename
            if data:
                if filename_pos is not None or namespace.filename_template:
                    if namespace.filename_template:
                        filename = CUSTOM_FORMATTER.format(
                            namespace.filename_template,
                            value=line[filename_pos] if filename_pos else None,
                            ext=result.meta['ext'],
                            line={h: line[i] for i, h in enumerate(input_headers)}
                        )
                    else:
                        filename = line[filename_pos] + result.meta['ext']
                else:
                    # NOTE: it would be nice to have an id that can be sorted by time
                    filename = str(uuid4()) + result.meta['ext']

            # Standardize encoding?
            encoding = result.meta['encoding']

            if data and namespace.standardize_encoding or namespace.contents_in_report:
                if encoding is None or encoding != 'utf-8' or namespace.contents_in_report:
                    data = data.decode(encoding, errors='replace')
                    encoding = 'utf-8'
                    content_write_flag = 'w'

            # Writing file on disk
            if data and not namespace.contents_in_report:

                if namespace.compress:
                    filename += '.gz'

                resource_path = join(namespace.output_dir, filename)
                resource_dir = dirname(resource_path)

                os.makedirs(resource_dir, exist_ok=True)

                with open(resource_path, content_write_flag) as f:

                    # TODO: what if standardize_encoding + compress?
                    f.write(gzip.compress(data) if namespace.compress else data)

            # Reporting in output
            resolved_url = response.geturl()

            write_output(
                line_index,
                line,
                resolved=resolved_url if resolved_url != result.url else None,
                status=response.status,
                filename=filename,
                encoding=encoding,
                data=data
            )

        # Handling potential errors
        else:
            error_code = report_error(result.error)

            write_output(
                line_index,
                line,
                error=error_code
            )

    # Closing files
    if namespace.output is not None:
        output_file.close()
