# =============================================================================
# Minet Fetch CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and fetching the urls found
# in the given column. This is done in a respectful multithreaded fashion to
# optimize both running time & memory.
#
import os
import gzip
import casanova
from io import StringIO
from os.path import join, dirname
from collections import Counter
from uuid import uuid4
from ural import is_shortened_url

from minet.fetch import multithreaded_fetch, multithreaded_resolve
from minet.utils import PseudoFStringFormatter
from minet.fs import FolderStrategy
from minet.web import (
    grab_cookies,
    parse_http_header
)
from minet.cli.constants import DEFAULT_PREBUFFER_BYTES
from minet.cli.reporters import report_error
from minet.cli.utils import LoadingBar, die


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


def fetch_action(cli_args, resolve=False):

    # If we are hitting a single url we enable contents_in_report by default
    if not resolve and isinstance(cli_args.file, StringIO) and cli_args.contents_in_report is None:
        cli_args.contents_in_report = True

    # Trying to instantiate the folder strategy
    if not resolve:
        folder_strategy = FolderStrategy.from_name(cli_args.folder_strategy)

        if folder_strategy is None:
            die([
                'Invalid "%s" --folder-strategy!' % cli_args.folder_strategy,
                'Check the list at the end of the command help:',
                '  $ minet fetch -h'
            ])

    # HTTP method
    http_method = cli_args.method

    # Cookie grabber
    get_cookie = None
    if cli_args.grab_cookies:
        get_cookie = grab_cookies(cli_args.grab_cookies)

    # Global headers
    global_headers = None
    if cli_args.headers:
        global_headers = {}

        for header in cli_args.headers:
            k, v = parse_http_header(header)
            global_headers[k] = v

    # Resume listener
    skipped_rows = 0
    resuming_reader_loading = None

    if cli_args.resume and cli_args.output.can_resume():
        resuming_reader_loading = LoadingBar(
            desc='Resuming',
            unit='line'
        )

        def output_read_listener(event, row):
            nonlocal skipped_rows

            if event != 'output.row':
                return

            skipped_rows += 1
            resuming_reader_loading.update()

        cli_args.output.listener = output_read_listener

    if resolve:
        additional_headers = RESOLVE_ADDITIONAL_HEADERS
    else:
        additional_headers = FETCH_ADDITIONAL_HEADERS

        if cli_args.contents_in_report:
            additional_headers = additional_headers + ['raw_contents']

    # Enricher
    enricher = casanova.threadsafe_enricher(
        cli_args.file,
        cli_args.output,
        add=additional_headers,
        keep=cli_args.select,
        total=cli_args.total,
        prebuffer_bytes=DEFAULT_PREBUFFER_BYTES
    )

    if resuming_reader_loading is not None:
        resuming_reader_loading.close()

    if cli_args.column not in enricher.pos:
        die([
            'Could not find the "%s" column containing the urls in the given CSV file.' % cli_args.column
        ])

    url_pos = enricher.pos[cli_args.column]

    filename_pos = None

    if not resolve and cli_args.filename is not None:
        if cli_args.filename not in enricher.pos:
            die([
                'Could not find the "%s" column containing the filenames in the given CSV file.' % cli_args.filename
            ])

        filename_pos = enricher.pos[cli_args.filename]

    # Loading bar
    loading_bar = LoadingBar(
        desc='Fetching pages',
        total=enricher.total,
        unit='url',
        initial=skipped_rows
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

        stats = {'errors': errors}

        for code, count in status_codes.most_common(1):
            stats[str(code)] = count

        loading_bar.update_stats(**stats)
        loading_bar.update()

    only_shortened = getattr(cli_args, 'only_shortened', False)

    def url_key(item):
        url = item[1][url_pos].strip()

        if not url:
            return

        if only_shortened and not is_shortened_url(url):
            return

        # Url templating
        if cli_args.url_template:
            return cli_args.url_template.format(value=url)

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

        if cli_args.contents_in_report:
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
        'insecure': cli_args.insecure,
        'threads': cli_args.threads,
        'throttle': cli_args.throttle,
        'domain_parallelism': cli_args.domain_parallelism,
        'max_redirects': cli_args.max_redirects
    }

    if cli_args.timeout is not None:
        common_kwargs['timeout'] = cli_args.timeout

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
                if not cli_args.keep_failed_contents and response.status != 200:
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
                    if filename_pos is not None or cli_args.filename_template:
                        root, ext = os.path.splitext(row[filename_pos]) if filename_pos is not None else (None, '')
                        ext = ext if ext else result.meta.get('ext', '')
                        if cli_args.filename_template:
                            filename = CUSTOM_FORMATTER.format(
                                cli_args.filename_template,
                                value=root,
                                ext=ext,
                                line=enricher.wrap(row)
                            )
                        else:
                            filename = root + ext
                    else:
                        # NOTE: it would be nice to have an id that can be sorted by time
                        filename = str(uuid4()) + result.meta.get('ext', '')

                    # Applying folder strategy
                    filename = folder_strategy.apply(
                        filename=filename,
                        url=result.response.geturl()
                    )

                # Standardize encoding?
                encoding = result.meta['encoding']

                if data and cli_args.standardize_encoding or cli_args.contents_in_report:
                    if encoding is None or encoding != 'utf-8' or cli_args.contents_in_report:
                        data = data.decode(encoding if encoding is not None else 'utf-8', errors='replace')
                        encoding = 'utf-8'
                        content_write_flag = 'w'

                # Writing file on disk
                if data and not cli_args.contents_in_report:

                    if cli_args.compress:
                        filename += '.gz'

                    resource_path = join(cli_args.output_dir, filename)
                    resource_dir = dirname(resource_path)

                    os.makedirs(resource_dir, exist_ok=True)

                    with open(resource_path, content_write_flag) as f:

                        # TODO: what if standardize_encoding + compress?
                        f.write(gzip.compress(data) if cli_args.compress else data)

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
            follow_meta_refresh=cli_args.follow_meta_refresh,
            follow_js_relocation=cli_args.follow_js_relocation,
            infer_redirection=cli_args.infer_redirection,
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
