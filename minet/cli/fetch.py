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
import certifi
from os.path import join
from urllib3 import PoolManager
from tqdm import tqdm
from quenouille import imap
from tld import get_fld
from uuid import uuid4
from ural import ensure_protocol

from urllib3.exceptions import (
    HTTPError,
    ConnectTimeoutError,
    MaxRetryError,
    ReadTimeoutError,
    ResponseError
)

from minet.cli.utils import custom_reader

OUTPUT_ADDITIONAL_HEADERS = ['status', 'error', 'filename']

# TODO: make this an option!
SPOOFED_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'

def max_retry_error_reporter(error):
    if isinstance(error, (ConnectTimeoutError, ReadTimeoutError)):
        return 'timeout'

    if isinstance(error.reason, ResponseError) and 'redirect' in repr(error.reason):
        return 'too-many-redirects'

    return 'max-retries-exceeded'

ERROR_REPORTERS = {
    MaxRetryError: max_retry_error_reporter
}


def domain_name(job):
    """
    Function returning the TLD from a job to guarantee max domain name
    concurrency in multithreaded logic.
    """
    return get_fld(job[2], fix_protocol=True)


def fetch(pool, url):
    try:
        r = pool.request(
            'GET',
            ensure_protocol(url),
            headers={
                'User-Agent': SPOOFED_UA
            }
        )

        return None, r
    except HTTPError as e:
        return e, None


def worker(job):
    """
    Function using the urllib3 pool to actually fetch our contents from the web.
    """
    pool, line, url = job

    error, result = fetch(pool, url)

    return error, url, line, result


def fetch_action(namespace):
    input_headers, pos, reader = custom_reader(namespace.file, namespace.column)
    filename_pos = input_headers.index(namespace.filename) if namespace.filename else filename_pos

    selected_fields = namespace.select.split(',') if namespace.select else None
    selected_pos = [input_headers.index(h) for h in selected_fields] if selected_fields else None

    # First we need to create the relevant directory
    os.makedirs(namespace.output_dir, exist_ok=True)

    # Reading output
    output_headers = (input_headers if not selected_pos else [input_headers[i] for i in selected_pos])
    output_headers += OUTPUT_ADDITIONAL_HEADERS
    output_file = open(namespace.output, 'w')
    output_writer = csv.writer(output_file)
    output_writer.writerow(output_headers)

    # Creating the http pool
    pool = PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    # Generator yielding urls to fetch
    def payloads():
        for line in reader:
            url = line[pos].strip()

            if not url:

                # TODO: this could desynchronize loading bar total
                continue

            yield (pool, line, url)

    # Streaming the file and fetching the url using multiple threads
    loading_bar = tqdm(
        payloads(),
        desc='Fetching pages',
        total=namespace.total,
        dynamic_ncols=True,
        unit=' urls'
    )

    multithreaded_iterator = imap(
        loading_bar,
        worker,
        namespace.threads,
        group=domain_name,
        group_parallelism=1,
        group_buffer_size=25,
        group_throttle=0.25
    )

    for error, url, line, result in multithreaded_iterator:

        # No error
        if error is None:

            filename = None

            # TODO: get correct extension!
            if filename_pos is not None:
                filename = line[filename_pos] + '.html'
            else:
                # NOTE: it would be nice to have an id that can be sorted by time
                filename = uuid4() + '.html'

            # Writing file on disk
            with open(join(namespace.output_dir, filename), 'wb') as f:
                f.write(result.data)

            # Reporting in output
            if selected_pos:
                line = [line[i] for i in selected_pos]

            line.extend([result.status, '', filename])
            output_writer.writerow(line)

        # Handling potential errors
        else:
            # loading_bar.write(repr(error))

            reporter = ERROR_REPORTERS.get(type(error), repr)

            # Reporting in output
            if selected_pos:
                line = [line[i] for i in selected_pos]

            line.extend(['', reporter(error), ''])
            output_writer.writerow(line)

    # Closing files
    output_file.close()
