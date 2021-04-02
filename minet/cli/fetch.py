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
from ural import (
    is_url,
    is_shortened_url
)

from minet.fetch import multithreaded_fetch, multithreaded_resolve
from minet.utils import PseudoFStringFormatter
from minet.fs import FolderStrategy
from minet.web import (
    grab_cookies,
    parse_http_header
)
from minet.cli.reporters import report_error
from minet.cli.utils import (
    open_output_file,
    die,
    edit_namespace_with_csv_io
)

FETCH_ADDITIONAL_HEADERS = [
    'resolved',
    'status',
    'error',
    'filename',
    'mimetype',
    'encoding'
]

RESOLVE_ADDITIONAL_HEADERS = [
    'resolved',
    'status',
    'error',
    'redirects',
    'chain'
]

CUSTOM_FORMATTER = PseudoFStringFormatter()


def fetch_action(namespace, resolve=False):

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
        if not resolve and namespace.contents_in_report is None:
            namespace.contents_in_report = True

    # Trying to instantiate the folder strategy
    if not resolve:
        folder_strategy = FolderStrategy.from_name(namespace.folder_strategy)

        if folder_strategy is None:
            die([
                'Invalid "%s" --folder-strategy!' % namespace.folder_strategy,
                'Check the list at the end of the command help:',
                '  $ minet fetch -h'
            ])

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

    if resolve:
        additional_headers = RESOLVE_ADDITIONAL_HEADERS
    else:
        additional_headers = FETCH_ADDITIONAL_HEADERS

        if namespace.contents_in_report:
            additional_headers = additional_headers + ['raw_contents']

    # Enricher
    enricher = casanova.threadsafe_enricher(
        namespace.file,
        output_file,
        resumable=resuming,
        auto_resume=False,
        add=additional_headers,
        keep=namespace.select,
        listener=listener
    )

    if namespace.column not in enricher.pos:
        die([
            'Could not find the "%s" column containing the urls in the given CSV file.' % namespace.column
        ])

    url_pos = enricher.pos[namespace.column]

    filename_pos = None

    if not resolve and namespace.filename is not None:
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

    def update_loading_bar(result):
        nonlocal errors

        if result.error is not None:
            errors += 1
        else:
            if resolve:
                status = result.stack[-1].status
            else:
                status = result.response.status

            if status >= 400:
                status_codes[status] += 1

        postfix = {'errors': errors}

        for code, count in status_codes.most_common(1):
            postfix[str(code)] = count

        loading_bar.set_postfix(**postfix)
        loading_bar.update()

    only_shortened = getattr(namespace, 'only_shortened', False)

    def url_key(item):
        url = item[1][url_pos].strip()

        if not url:
            return

        if only_shortened and not is_shortened_url(url):
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

    def write_fetch_output(index, row, resolved=None, status=None, error=None,
                           filename=None, encoding=None, mimetype=None, data=None):

        addendum = [
            resolved or '',
            status or '',
            error or '',
            filename or '',
            mimetype or '',
            encoding or ''
        ]

        if namespace.contents_in_report:
            addendum.append(data or '')

        enricher.writerow(index, row, addendum)

    def write_resolve_output(index, row, resolved=None, status=None, error=None,
                             redirects=None, chain=None):
        addendum = [
            resolved or '',
            status or '',
            error or '',
            redirects or '',
            chain or ''
        ]

        enricher.writerow(index, row, addendum)

    errors = 0
    status_codes = Counter()

    common_kwargs = {
        'key': url_key,
        'insecure': namespace.insecure,
        'threads': namespace.threads,
        'throttle': namespace.throttle,
        'domain_parallelism': namespace.domain_parallelism,
        'max_redirects': namespace.max_redirects
    }

    if namespace.timeout is not None:
        common_kwargs['timeout'] = namespace.timeout

    # Normal fetch
    if not resolve:

        multithreaded_iterator = multithreaded_fetch(
            enricher,
            request_args=request_args,
            **common_kwargs
        )

        for result in multithreaded_iterator:
            index, row = result.item

            if not result.url:

                write_fetch_output(
                    index,
                    row
                )

                loading_bar.update()
                continue

            response = result.response
            data = response.data if response is not None else None

            content_write_flag = 'wb'

            # Updating stats
            update_loading_bar(result)

            # No error
            if result.error is None:

                # Final url target
                resolved_url = response.geturl()

                if resolved_url == result.url:
                    resolved_url = None

                # Should we keep downloaded content?
                if not namespace.keep_failed_contents and response.status != 200:
                    write_fetch_output(
                        index,
                        row,
                        resolved=resolved_url,
                        status=response.status
                    )
                    continue

                filename = None

                # Building filename
                if data:
                    if filename_pos is not None or namespace.filename_template:
                        root, ext = os.path.splitext(row[filename_pos]) if filename_pos is not None else (None, '')
                        ext = ext if ext else result.meta['ext']
                        if namespace.filename_template:
                            filename = CUSTOM_FORMATTER.format(
                                namespace.filename_template,
                                value=root,
                                ext=ext,
                                line=enricher.wrap(row)
                            )
                        else:
                            filename = root + ext
                    else:
                        # NOTE: it would be nice to have an id that can be sorted by time
                        filename = str(uuid4()) + result.meta['ext']

                    # Applying folder strategy
                    filename = folder_strategy.apply(
                        filename=filename,
                        url=result.response.geturl()
                    )

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
                write_fetch_output(
                    index,
                    row,
                    resolved=resolved_url,
                    status=response.status,
                    filename=filename,
                    encoding=encoding,
                    mimetype=result.meta['mimetype'],
                    data=data
                )

            # Handling potential errors
            else:
                error_code = report_error(result.error)

                write_fetch_output(
                    index,
                    row,
                    error=error_code
                )

    # Resolve
    else:

        multithreaded_iterator = multithreaded_resolve(
            enricher,
            resolve_args=request_args,
            follow_meta_refresh=namespace.follow_meta_refresh,
            follow_js_relocation=namespace.follow_js_relocation,
            infer_redirection=namespace.infer_redirection,
            **common_kwargs
        )

        for result in multithreaded_iterator:
            index, row = result.item

            if not result.url:

                write_resolve_output(
                    index,
                    row
                )

                loading_bar.update()
                continue

            # Updating stats
            update_loading_bar(result)

            # No error
            if result.error is None:

                # Reporting in output
                last = result.stack[-1]

                write_resolve_output(
                    index,
                    row,
                    resolved=last.url,
                    status=last.status,
                    redirects=len(result.stack) - 1,
                    chain='|'.join(step.type for step in result.stack)
                )

            # Handling potential errors
            else:
                error_code = report_error(result.error)

                write_resolve_output(
                    index,
                    row,
                    error=error_code,
                    redirects=(len(result.stack) - 1) if result.stack else None,
                    chain='|'.join(step.type for step in result.stack) if result.stack else None
                )

    # Closing files
    output_file.close()
