# =============================================================================
# Minet Fetch CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and fetching the urls found
# in the given column. This is done in a respectful multithreaded fashion to
# optimize both running time & memory.
#
import os
import certifi
from os.path import join
from urllib3 import PoolManager
from urllib3.exceptions import HTTPError
from tqdm import tqdm
from quenouille import imap
from tld import get_fld
from uuid import uuid4
from ural import ensure_protocol

from minet.cli.utils import custom_reader


def domain_name(job):
    """
    Function returning the TLD from a job to guarantee max domain name
    concurrency in multithreaded logic.
    """
    return get_fld(job[2], fix_protocol=True)


def fetch(pool, url):
    try:
        r = pool.request('GET', ensure_protocol(url))
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

    # First we need to create the relevant directory
    os.makedirs(namespace.output_dir, exist_ok=True)

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
    loading_bar = tqdm(payloads(), total=namespace.total)

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

            # NOTE: it would be nice to have an id that can be sorted by time
            uuid = uuid4()

            # Writing file on disk
            # TODO: get correct extension!
            loading_bar.write(url)
            with open(join(namespace.output_dir, '%s.html' % uuid), 'wb') as f:
                f.write(result.data)

        # Handling potential errors
        else:
            loading_bar.write(repr(error))
