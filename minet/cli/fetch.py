# =============================================================================
# Minet Fetch CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and fetching the urls found
# in the given column. This is done in a respectful multithreaded fashion to
# optimize both running time & memory.
#
import os
import sys
import gzip
import casanova
from os.path import join, dirname, isfile
from collections import Counter
from tqdm import tqdm
from uuid import uuid4
from ural import is_url

from minet.fetch import multithreaded_fetch
from minet.utils import (
    grab_cookies,
    parse_http_header,
    PseudoFStringFormatter
)
from minet.cli.reporters import report_error
from minet.cli.utils import (
    open_output_file,
    die,
    LazyLineDict,
    edit_namespace_with_csv_io
)

OUTPUT_ADDITIONAL_HEADERS = [
    'resolved',
    'status',
    'error',
    'filename',
    'encoding'
]

CUSTOM_FORMATTER = PseudoFStringFormatter()


def fetch_action(namespace):

    # Are we resuming
    resuming = namespace.resume

    if resuming and not namespace.output:
        die([
            'Cannot --resume without specifying -o/--output.'
        ])

    # Do we need to fetch only a single url?
    single_url = namespace.file is sys.stdin and is_url(namespace.column)

    if single_url:
        edit_namespace_with_csv_io(namespace, 'url')

        # If we are hitting a single url we enable contents_in_report
        if namespace.contents_in_report is None:
            namespace.contents_in_report = True

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
            global_headers[k] = v

    flag = 'w'
    if namespace.output is not None and resuming and isfile(namespace.output):
        flag = 'r+'

    output_file = open_output_file(namespace.output, flag=flag)

    # Resume listener
    listener = None
    resuming_reader_loading = None
    skipped = 0

    if resuming:
        resuming_reader_loading = tqdm(
            desc='Resuming',
            dynamic_ncols=True,
            unit=' lines'
        )

        def listener(event, row):
            nonlocal skipped

            if event == 'resume.output':
                resuming_reader_loading.update()

            if event == 'resume.input':
                skipped += 1
                loading_bar.set_postfix(skipped=skipped)
                loading_bar.update()

    # Enricher
    enricher = casanova.threadsafe_enricher(
        namespace.file,
        output_file,
        resumable=resuming,
        auto_resume=False,
        add=OUTPUT_ADDITIONAL_HEADERS + (['raw_contents'] if namespace.contents_in_report else []),
        keep=namespace.select,
        listener=listener
    )

    if namespace.column not in enricher.pos:
        die([
            'Could not find the "%s" column containing the urls in the given CSV file.' % namespace.column
        ])

    url_pos = enricher.pos[namespace.column]

    filename_pos = None

    if namespace.filename is not None:
        if namespace.filename not in enricher.pos:
            die([
                'Could not find the "%s" column containing the filenames in the given CSV file.' % namespace.filename
            ])

        filename_pos = enricher.pos[namespace.filename]

    indexed_input_headers = {h: i for i, h in enumerate(enricher.fieldnames)}

    if resuming:
        enricher.resume()
        resuming_reader_loading.close()

    # Loading bar
    total = namespace.total

    loading_bar = tqdm(
        desc='Fetching pages',
        total=total,
        dynamic_ncols=True,
        unit=' urls'
    )

    def url_key(item):
        url = item[1][url_pos].strip()

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

    def write_output(index, row, resolved=None, status=None, error=None,
                     filename=None, encoding=None, data=None):

        addendum = [
            resolved or '',
            status or '',
            error or '',
            filename or '',
            encoding or ''
        ]

        if namespace.contents_in_report:
            addendum.append(data or '')

        enricher.writerow(index, row, addendum)

    errors = 0
    status_codes = Counter()

    fetch_kwargs = {
        'threads': namespace.threads,
        'throttle': namespace.throttle,
        'domain_parallelism': namespace.domain_parallelism
    }

    if namespace.timeout is not None:
        fetch_kwargs['timeout'] = namespace.timeout

    multithreaded_iterator = multithreaded_fetch(
        enricher,
        key=url_key,
        request_args=request_args,
        **fetch_kwargs
    )

    for result in multithreaded_iterator:
        index, row = result.item

        if not result.url:

            write_output(
                index,
                row
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
                            value=row[filename_pos] if filename_pos is not None else None,
                            ext=result.meta['ext'],
                            line=LazyLineDict(indexed_input_headers, row)
                        )
                    else:
                        filename = row[filename_pos] + result.meta['ext']
                else:
                    # NOTE: it would be nice to have an id that can be sorted by time
                    filename = str(uuid4()) + result.meta['ext']

            # Standardize encoding?
            encoding = result.meta['encoding']

            if data and namespace.standardize_encoding or namespace.contents_in_report:
                if encoding is None or encoding != 'utf-8' or namespace.contents_in_report:
                    data = data.decode(encoding if encoding is not None else 'utf-8', errors='replace')
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
                index,
                row,
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
                index,
                row,
                error=error_code
            )

    # Closing files
    output_file.close()
