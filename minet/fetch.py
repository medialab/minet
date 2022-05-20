# =============================================================================
# Minet Multithreaded Fetch
# =============================================================================
#
# Exposing a specialized quenouille wrapper grabbing various urls from the
# web in a multithreaded fashion.
#
from collections import namedtuple
from quenouille import ThreadPoolExecutor
from ural import get_domain_name, ensure_protocol

from minet.web import create_pool, request, resolve, extract_response_meta
from minet.heuristics import should_spoof_ua_when_resolving
from minet.constants import (
    DEFAULT_DOMAIN_PARALLELISM,
    DEFAULT_IMAP_BUFFER_SIZE,
    DEFAULT_THROTTLE,
    DEFAULT_URLLIB3_TIMEOUT,
    DEFAULT_FETCH_MAX_REDIRECTS,
    DEFAULT_RESOLVE_MAX_REDIRECTS,
)

FetchWorkerPayload = namedtuple("FetchWorkerPayload", ["item", "domain", "url"])


class FetchResult(object):
    __slots__ = ("item", "domain", "url", "error", "response", "meta")

    def __init__(self, item, domain, url):
        self.item = item
        self.domain = domain
        self.url = url
        self.error = None
        self.response = None
        self.meta = {}

    def __repr__(self):
        name = self.__class__.__name__

        if not self.url:
            return "<{name} empty!>".format(name=name)

        return "<{name}{errored} url={url!r} status={status!r} ext={ext!r} encoding={encoding!r}>".format(
            name=name,
            url=self.url,
            status=self.response.status if self.response else None,
            ext=self.meta.get("ext"),
            encoding=self.meta.get("encoding"),
            errored=" errored!" if self.error else "",
        )

    @property
    def resolved(self):
        if self.response is None:
            return None

        return self.response.geturl()


class ResolveResult(object):
    __slots__ = ("item", "domain", "url", "error", "stack")

    def __init__(self, item, domain, url):
        self.item = item
        self.domain = domain
        self.url = url
        self.error = None
        self.stack = None

    def __repr__(self):
        name = self.__class__.__name__

        if not self.url:
            return "<{name} empty!>".format(name=name)

        return "<{name}{errored} url={url!r} status={status!r} redirects={redirects!r}>".format(
            name=name,
            url=self.url,
            status=self.stack[-1].status if self.stack else None,
            redirects=(len(self.stack) - 1) if self.stack else 0,
            errored=" errored!" if self.error else "",
        )


def key_by_domain_name(payload):
    return payload.domain


def payloads_iter(iterator, key=None):
    for item in iterator:
        url = item if key is None else key(item)

        if not url:
            yield FetchWorkerPayload(item=item, domain=None, url=None)

            continue

        # Url cleanup
        url = ensure_protocol(url.strip())

        yield FetchWorkerPayload(item=item, domain=get_domain_name(url), url=url)


class FetchWorker(object):
    def __init__(
        self,
        pool,
        *,
        request_args=None,
        max_redirects=DEFAULT_FETCH_MAX_REDIRECTS,
        callback=None
    ):
        self.pool = pool
        self.request_args = request_args
        self.max_redirects = max_redirects
        self.callback = callback

    def __call__(self, payload):
        item, domain, url = payload

        result = FetchResult(*payload)

        if url is None:
            return result

        # NOTE: request_args must be threadsafe
        kwargs = {}

        if self.request_args is not None:
            kwargs = self.request_args(domain, url, item)

        error, response = request(
            url, pool=self.pool, max_redirects=self.max_redirects, **kwargs
        )

        if error:
            result.error = error
        else:

            # Forcing urllib3 to read data in thread
            # TODO: this is probably useless and should be replaced by preload_content at the right place
            data = response.data

            # Meta
            meta = extract_response_meta(response)

            result.response = response
            result.meta = meta

            if self.callback is not None:
                self.callback(result)

        return result


class ResolveWorker(object):
    def __init__(
        self,
        pool,
        *,
        resolve_args=None,
        max_redirects=DEFAULT_RESOLVE_MAX_REDIRECTS,
        follow_refresh_header=True,
        follow_meta_refresh=False,
        follow_js_relocation=False,
        infer_redirection=False,
        canonicalize=False
    ):

        self.pool = pool
        self.resolve_args = resolve_args
        self.max_redirects = max_redirects
        self.follow_refresh_header = follow_refresh_header
        self.follow_meta_refresh = follow_meta_refresh
        self.follow_js_relocation = follow_js_relocation
        self.infer_redirection = infer_redirection
        self.canonicalize = canonicalize

    def __call__(self, payload):
        item, domain, url = payload

        result = ResolveResult(*payload)

        if url is None:
            return result

        # NOTE: resolve_args must be threadsafe
        kwargs = {}

        if self.resolve_args is not None:
            kwargs = self.resolve_args(domain, url, item)

        # NOTE: should it be just in the CLI?
        if "spoof_ua" not in kwargs:
            kwargs["spoof_ua"] = should_spoof_ua_when_resolving(domain)

        error, stack = resolve(
            url,
            pool=self.pool,
            max_redirects=self.max_redirects,
            follow_refresh_header=self.follow_refresh_header,
            follow_meta_refresh=self.follow_meta_refresh,
            follow_js_relocation=self.follow_js_relocation,
            infer_redirection=self.infer_redirection,
            canonicalize=self.canonicalize,
            **kwargs
        )

        result.error = error
        result.stack = stack

        return result


class HTTPThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(
        self,
        max_workers=None,
        insecure=False,
        timeout=DEFAULT_URLLIB3_TIMEOUT,
        **kwargs
    ):
        super().__init__(max_workers, **kwargs)
        self.pool = create_pool(threads=max_workers, insecure=insecure, timeout=timeout)

    def imap(self, *args, **kwargs):
        raise NotImplementedError


class FetchThreadPoolExecutor(HTTPThreadPoolExecutor):
    def imap_unordered(
        self,
        iterator,
        *,
        key=None,
        throttle=DEFAULT_THROTTLE,
        request_args=None,
        buffer_size=DEFAULT_IMAP_BUFFER_SIZE,
        domain_parallelism=DEFAULT_DOMAIN_PARALLELISM,
        max_redirects=DEFAULT_FETCH_MAX_REDIRECTS,
        callback=None
    ):

        # TODO: validate
        iterator = payloads_iter(iterator, key=key)
        worker = FetchWorker(
            self.pool,
            request_args=request_args,
            max_redirects=max_redirects,
            callback=callback,
        )

        return super().imap_unordered(
            iterator,
            worker,
            key=key_by_domain_name,
            parallelism=domain_parallelism,
            buffer_size=buffer_size,
            throttle=throttle,
        )


class ResolveThreadPoolExecutor(HTTPThreadPoolExecutor):
    def imap_unordered(
        self,
        iterator,
        *,
        key=None,
        throttle=DEFAULT_THROTTLE,
        resolve_args=None,
        buffer_size=DEFAULT_IMAP_BUFFER_SIZE,
        domain_parallelism=DEFAULT_DOMAIN_PARALLELISM,
        max_redirects=DEFAULT_FETCH_MAX_REDIRECTS,
        follow_refresh_header=True,
        follow_meta_refresh=False,
        follow_js_relocation=False,
        infer_redirection=False,
        canonicalize=False
    ):

        # TODO: validate
        iterator = payloads_iter(iterator, key=key)
        worker = ResolveWorker(
            self.pool,
            resolve_args=resolve_args,
            max_redirects=max_redirects,
            follow_refresh_header=follow_refresh_header,
            follow_meta_refresh=follow_meta_refresh,
            follow_js_relocation=follow_js_relocation,
            infer_redirection=infer_redirection,
            canonicalize=canonicalize,
        )

        return super().imap_unordered(
            iterator,
            worker,
            key=key_by_domain_name,
            parallelism=domain_parallelism,
            buffer_size=buffer_size,
            throttle=throttle,
        )


def multithreaded_fetch(
    iterator,
    key=None,
    request_args=None,
    threads=25,
    throttle=DEFAULT_THROTTLE,
    buffer_size=DEFAULT_IMAP_BUFFER_SIZE,
    insecure=False,
    timeout=DEFAULT_URLLIB3_TIMEOUT,
    domain_parallelism=DEFAULT_DOMAIN_PARALLELISM,
    max_redirects=5,
    wait=True,
    daemonic=False,
    callback=None,
):
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

    def generator():
        with FetchThreadPoolExecutor(
            max_workers=threads,
            insecure=insecure,
            timeout=timeout,
            wait=wait,
            daemonic=daemonic,
        ) as executor:
            yield from executor.imap_unordered(
                iterator,
                key=key,
                throttle=throttle,
                request_args=request_args,
                buffer_size=buffer_size,
                domain_parallelism=domain_parallelism,
                max_redirects=max_redirects,
                callback=callback,
            )

    return generator()


def multithreaded_resolve(
    iterator,
    key=None,
    resolve_args=None,
    threads=25,
    throttle=DEFAULT_THROTTLE,
    max_redirects=5,
    follow_refresh_header=True,
    follow_meta_refresh=False,
    follow_js_relocation=False,
    infer_redirection=False,
    canonicalize=False,
    buffer_size=DEFAULT_IMAP_BUFFER_SIZE,
    insecure=False,
    timeout=DEFAULT_URLLIB3_TIMEOUT,
    domain_parallelism=DEFAULT_DOMAIN_PARALLELISM,
    wait=True,
    daemonic=False,
):
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
        follow_js_relocation (bool, optional): Whether to follow js relocation.
            Defaults to False.
        infer_redirection (bool, optional): Whether to infer redirections
            heuristically from urls. Defaults to False.
        canonicalize (bool, optional): Whether to extract the canonical url found
            in the html of the web page. Defaults to False.
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

    def generator():
        with ResolveThreadPoolExecutor(
            max_workers=threads,
            insecure=insecure,
            timeout=timeout,
            wait=wait,
            daemonic=daemonic,
        ) as executor:
            yield from executor.imap_unordered(
                iterator,
                key=key,
                throttle=throttle,
                resolve_args=resolve_args,
                buffer_size=buffer_size,
                domain_parallelism=domain_parallelism,
                max_redirects=max_redirects,
                follow_refresh_header=follow_refresh_header,
                follow_meta_refresh=follow_meta_refresh,
                follow_js_relocation=follow_js_relocation,
                infer_redirection=infer_redirection,
                canonicalize=canonicalize,
            )

    return generator()
