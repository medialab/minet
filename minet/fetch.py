# =============================================================================
# Minet Multithreaded Fetch
# =============================================================================
#
# Exposing a specialized quenouille wrapper grabbing various urls from the
# web in a multithreaded fashion.
#
from collections import namedtuple
from quenouille import imap_unordered
from ural import get_domain_name, ensure_protocol

from minet.web import (
    create_pool,
    request,
    resolve,
    extract_response_meta
)

from minet.constants import (
    DEFAULT_GROUP_PARALLELISM,
    DEFAULT_GROUP_BUFFER_SIZE,
    DEFAULT_THROTTLE,
    DEFAULT_URLLIB3_TIMEOUT
)

FetchWorkerPayload = namedtuple(
    'FetchWorkerPayload',
    [
        'item',
        'url'
    ]
)

FetchWorkerResult = namedtuple(
    'FetchWorkerResult',
    [
        'url',
        'item',
        'error',
        'response',
        'meta'
    ]
)

ResolveWorkerResult = namedtuple(
    'ResolveWorkerResult',
    [
        'url',
        'item',
        'error',
        'stack'
    ]
)


def multithreaded_fetch(iterator, key=None, request_args=None, threads=25,
                        throttle=DEFAULT_THROTTLE, guess_extension=True,
                        guess_encoding=True, buffer_size=DEFAULT_GROUP_BUFFER_SIZE,
                        insecure=False, timeout=DEFAULT_URLLIB3_TIMEOUT,
                        domain_parallelism=DEFAULT_GROUP_PARALLELISM,
                        max_redirects=5):
    """
    Function returning a multithreaded iterator over fetched urls.

    Args:
        iterator (iterable): An iterator over urls or arbitrary items.
        key (callable, optional): Function extracting url from yielded items.
        request_args (callable, optional): Function returning specific
            arguments to pass to the request util per yielded item.
        threads (int, optional): Number of threads to use. Defaults to 25.
        throttle (float or callable, optional): Per-domain throttle in seconds.
            Or a function taking domain name and item and returning the
            throttle to apply. Defaults to 0.2.
        max_redirects (int, optional): Max number of redirections to follow.
        guess_extension (bool, optional): Attempt to guess the resource's
            extension? Defaults to True.
        guess_encoding (bool, optional): Attempt to guess the resource's
            encoding? Defaults to True.
        domain_parallelism (int, optional): Max number of urls per domain to
            hit at the same time. Defaults to 1.
        buffer_size (int, optional): Max number of items per domain to enqueue
            into memory in hope of finding a new domain that can be processed
            immediately. Defaults to 1.
        insecure (bool, optional): Whether to ignore SSL certification errors
            when performing requests. Defaults to False.
        timeout (float or urllib3.Timeout, optional): Custom timeout for every
            request.

    Yields:
        FetchWorkerResult

    """

    # Creating the http pool manager
    pool = create_pool(threads=threads, insecure=insecure, timeout=timeout)

    # Thread worker
    def worker(payload):
        item, url = payload

        if url is None:
            return FetchWorkerResult(
                url=None,
                item=item,
                response=None,
                error=None,
                meta=None
            )

        kwargs = request_args(url, item) if request_args is not None else {}

        error, response = request(
            url,
            pool=pool,
            max_redirects=max_redirects,
            **kwargs
        )

        if error:
            return FetchWorkerResult(
                url=url,
                item=item,
                response=response,
                error=error,
                meta=None
            )

        # Forcing urllib3 to read data in thread
        # TODO: this is probably useless and should be replaced by preload_content at the right place
        data = response.data

        # Meta
        meta = extract_response_meta(
            response,
            guess_encoding=guess_encoding,
            guess_extension=guess_extension
        )

        return FetchWorkerResult(
            url=url,
            item=item,
            response=response,
            error=error,
            meta=meta
        )

    # Group resolver
    def grouper(payload):
        if payload.url is None:
            return

        return get_domain_name(payload.url)

    # Thread payload iterator
    def payloads():
        for item in iterator:
            url = item if key is None else key(item)

            if not url:
                yield FetchWorkerPayload(
                    item=item,
                    url=None
                )

                continue

            # Url cleanup
            url = ensure_protocol(url.strip())

            yield FetchWorkerPayload(
                item=item,
                url=url
            )

    def get_throttle(group, job):
        if group is None:
            return 0

        return throttle

    return imap_unordered(
        payloads(),
        worker,
        threads,
        group=grouper,
        group_parallelism=domain_parallelism,
        group_buffer_size=buffer_size,
        group_throttle=get_throttle
    )


def multithreaded_resolve(iterator, key=None, resolve_args=None, threads=25,
                          throttle=DEFAULT_THROTTLE, max_redirects=5,
                          follow_refresh_header=True, follow_meta_refresh=False,
                          follow_js_relocation=False, infer_redirection=False,
                          buffer_size=DEFAULT_GROUP_BUFFER_SIZE,
                          insecure=False, timeout=DEFAULT_URLLIB3_TIMEOUT,
                          domain_parallelism=DEFAULT_GROUP_PARALLELISM):
    """
    Function returning a multithreaded iterator over resolved urls.

    Args:
        iterator (iterable): An iterator over urls or arbitrary items.
        key (callable, optional): Function extracting url from yielded items.
        resolve_args (callable, optional): Function returning specific
            arguments to pass to the resolve util per yielded item.
        threads (int, optional): Number of threads to use. Defaults to 25.
        throttle (float or callable, optional): Per-domain throttle in seconds.
            Or a function taking domain name and item and returning the
            throttle to apply. Defaults to 0.2.
        max_redirects (int, optional): Max number of redirections to follow.
        follow_refresh_header (bool, optional): Whether to follow refresh
            headers. Defaults to True.
        follow_meta_refresh (bool, optional): Whether to follow meta refresh.
            Defaults to False.
        infer_redirection (bool, optional): Whether to infer redirections
            heuristically from urls. Defaults to False.
        buffer_size (int, optional): Max number of items per domain to enqueue
            into memory in hope of finding a new domain that can be processed
            immediately. Defaults to 1.
        insecure (bool, optional): Whether to ignore SSL certification errors
            when performing requests. Defaults to False.
        timeout (float or urllib3.Timeout, optional): Custom timeout for every
            request.
        domain_parallelism (int, optional): Max number of urls per domain to
            hit at the same time. Defaults to 1.

    Yields:
        ResolveWorkerResult

    """

    # Creating the http pool manager
    pool = create_pool(threads=threads, insecure=insecure, timeout=timeout)

    # Thread worker
    def worker(payload):
        item, url = payload

        if url is None:
            return ResolveWorkerResult(
                url=None,
                item=item,
                error=None,
                stack=None
            )

        kwargs = resolve_args(url, item) if resolve_args is not None else {}

        error, stack = resolve(
            url,
            pool=pool,
            max_redirects=max_redirects,
            follow_refresh_header=follow_refresh_header,
            follow_meta_refresh=follow_meta_refresh,
            follow_js_relocation=follow_js_relocation,
            infer_redirection=infer_redirection,
            **kwargs
        )

        return ResolveWorkerResult(
            url=url,
            item=item,
            error=error,
            stack=stack
        )

    # Group resolver
    def grouper(payload):
        if payload.url is None:
            return

        return get_domain_name(payload.url)

    # Thread payload iterator
    def payloads():
        for item in iterator:
            url = item if key is None else key(item)

            if not url:
                yield FetchWorkerPayload(
                    item=item,
                    url=None
                )

                continue

            # Url cleanup
            url = ensure_protocol(url.strip())

            yield FetchWorkerPayload(
                item=item,
                url=url
            )

    def get_throttle(group, job):
        if group is None:
            return 0

        return throttle

    return imap_unordered(
        payloads(),
        worker,
        threads,
        group=grouper,
        group_parallelism=domain_parallelism,
        group_buffer_size=buffer_size,
        group_throttle=get_throttle
    )
