# =============================================================================
# Minet Utils
# =============================================================================
#
# Miscellaneous helper function used throughout the library.
#
import re
import cgi
import certifi
import browser_cookie3
import hashlib
import urllib3
import json
import yaml
import time
import string
import mimetypes
import functools
import cchardet as chardet
from random import uniform
from collections import OrderedDict
from json.decoder import JSONDecodeError
from ural import is_url
from urllib.parse import urljoin
from urllib3 import HTTPResponse
from urllib.request import Request

from minet.encodings import is_supported_encoding

from minet.exceptions import (
    MaxRedirectsError,
    InfiniteRedirectsError,
    InvalidRedirectError,
    InvalidURLError,
    SelfRedirectError
)

from minet.constants import (
    DEFAULT_SPOOFED_UA,
    DEFAULT_URLLIB3_TIMEOUT,
    COOKIE_BROWSERS
)

mimetypes.init()

# Handy regexes
CHARSET_RE = re.compile(rb'<meta.*?charset=["\']*(.+?)["\'>]', flags=re.I)
PRAGMA_RE = re.compile(rb'<meta.*?content=["\']*;?charset=(.+?)["\'>]', flags=re.I)
XML_RE = re.compile(rb'^<\?xml.*?encoding=["\']*(.+?)["\'>]', flags=re.I)
NOSCRIPT_RE = re.compile(rb'<noscript[^>]*>.*</noscript[^>]*>', flags=re.I)
META_REFRESH_RE = re.compile(rb'''<meta\s+http-equiv=['"]?refresh['"]?\s+content=['"]?([^"']+)['">]?''', flags=re.I)
JAVASCRIPT_LOCATION_RE = re.compile(rb'''(?:window\.)?location(?:\s*=\s*|\.replace\(\s*)['"`](.*?)['"`]''')
ESCAPED_SLASH_RE = re.compile(rb'\\\/')
ASCII_RE = re.compile(r'^[ -~]*$')
DOUBLE_QUOTES_RE = re.compile(r'"')

# Constants
CHARDET_CONFIDENCE_THRESHOLD = 0.9
REDIRECT_STATUSES = set(HTTPResponse.REDIRECT_STATUSES)


def md5(string):
    h = hashlib.md5()
    h.update(string.encode())
    return h.hexdigest()


def fix_ensure_ascii_json_string(s):
    try:
        return json.loads('"%s"' % DOUBLE_QUOTES_RE.sub('\\"', s))
    except:
        return s


# TODO: add a version that tallies the possibilities
def guess_response_encoding(response, is_xml=False, use_chardet=False):
    """
    Function taking an urllib3 response object and attempting to guess its
    encoding.
    """
    content_type_header = response.getheader('content-type')

    suboptimal_charset = None

    if content_type_header is not None:
        parsed_header = cgi.parse_header(content_type_header)

        if len(parsed_header) > 1:
            charset = parsed_header[1].get('charset')

            if charset is not None:
                if is_supported_encoding(charset):
                    return charset.lower()
                else:
                    suboptimal_charset = charset

    data = response.data

    # Data is empty
    if not data.strip():
        return None

    # TODO: use re.search to go faster!
    if is_xml:
        matches = re.findall(CHARSET_RE, data)

        if len(matches) == 0:
            matches = re.findall(PRAGMA_RE, data)

        if len(matches) == 0:
            matches = re.findall(XML_RE, data)

        # NOTE: here we are returning the last one, but we could also use
        # frequency at the expense of performance
        if len(matches) != 0:
            charset = matches[-1].lower().decode()

            if is_supported_encoding(charset):
                return charset
            else:
                suboptimal_charset = charset

    if use_chardet:
        chardet_result = chardet.detect(data)

        # Could not detect anything
        if (
            not chardet_result or
            chardet_result.get('confidence') is None
        ):
            return None

        if chardet_result['confidence'] >= CHARDET_CONFIDENCE_THRESHOLD:
            return chardet_result['encoding'].lower()

    return suboptimal_charset


def parse_http_header(header):
    key, value = header.split(':', 1)

    return key.strip(), value.strip()


# TODO: take more cases into account...
#   http://www.otsukare.info/2015/03/26/refresh-http-header
def parse_http_refresh(value):
    try:

        if isinstance(value, bytes):
            value = value.decode()

        duration, url = value.strip().split(';', 1)

        if not url.lower().strip().startswith('url='):
            return None

        return int(duration), str(url.split('=', 1)[1])
    except:
        return None


def find_meta_refresh(html_chunk):
    m = META_REFRESH_RE.search(html_chunk)

    if not m:
        return None

    return parse_http_refresh(m.group(1))


def find_javascript_relocation(html_chunk):
    m = JAVASCRIPT_LOCATION_RE.search(html_chunk)

    if not m:
        return None

    try:
        return ESCAPED_SLASH_RE.sub(b'/', m.group(1)).decode()
    except:
        return None


class CookieResolver(object):
    def __init__(self, jar):
        self.jar = jar

    def __call__(self, url):
        req = Request(url)
        self.jar.add_cookie_header(req)

        return req.get_header('Cookie') or None


def grab_cookies(browser='firefox'):
    if browser not in COOKIE_BROWSERS:
        raise TypeError('minet.utils.grab_cookies: unknown "%s" browser.' % browser)

    try:
        return CookieResolver(getattr(browser_cookie3, browser)())
    except browser_cookie3.BrowserCookieError:
        return None


def dict_to_cookie_string(d):
    return '; '.join('%s=%s' % r for r in d.items())


def create_pool(proxy=None, threads=None, insecure=False, **kwargs):
    """
    Helper function returning a urllib3 pool manager with sane defaults.
    """

    manager_kwargs = {
        'timeout': DEFAULT_URLLIB3_TIMEOUT
    }

    if not insecure:
        manager_kwargs['cert_reqs'] = 'CERT_REQUIRED'
        manager_kwargs['ca_certs'] = certifi.where()
    else:
        manager_kwargs['cert_reqs'] = 'CERT_NONE'
        # manager_kwargs['assert_hostname'] = False

        urllib3.disable_warnings()

    if threads is not None:

        # TODO: maxsize should increase with group_parallelism
        manager_kwargs['maxsize'] = 1
        manager_kwargs['num_pools'] = threads * 2

    manager_kwargs.update(kwargs)

    if proxy is not None:
        return urllib3.ProxyManager(proxy, **manager_kwargs)

    return urllib3.PoolManager(**manager_kwargs)


def raw_request(http, url, method='GET', headers=None,
                preload_content=True, release_conn=True, timeout=None,
                body=None):
    """
    Generic request helpers using a urllib3 pool to access some resource.
    """

    # Validating URL
    if not is_url(url, require_protocol=True, tld_aware=True, allow_spaces_in_path=True):
        return InvalidURLError('Invalid URL'), None

    # Performing request
    request_kwargs = {
        'headers': headers,
        'body': body,
        'preload_content': preload_content,
        'release_conn': release_conn,
        'redirect': False,
        'retries': False
    }

    if timeout is not None:
        request_kwargs['timeout'] = timeout

    try:
        response = http.request(
            method,
            url,
            **request_kwargs
        )
    except Exception as e:
        return e, None

    return None, response


class Redirection(object):
    __slots__ = ('status', 'type', 'url')

    def __init__(self, url):
        self.status = None
        self.url = url
        self.type = 'hit'

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s type=%(type)s status=%(status)s url=%(url)s>'
        ) % {
            'class_name': class_name,
            'type': self.type,
            'status': self.status,
            'url': self.url
        }


def raw_resolve(http, url, method='GET', headers=None, max_redirects=5,
                follow_refresh_header=True, follow_meta_refresh=False,
                follow_js_relocation=False, return_response=False, timeout=None,
                body=None):
    """
    Helper function attempting to resolve the given url.
    """

    url_stack = OrderedDict()
    error = None
    response = None

    for _ in range(max_redirects):

        if response:
            response.release_conn()
            response.close()

        http_error, response = raw_request(
            http,
            url,
            method=method,
            headers=headers,
            body=body,
            preload_content=False,
            release_conn=False,
            timeout=timeout
        )

        redirection = Redirection(url)

        # Request error
        if http_error:
            redirection.type = 'error'
            url_stack[url] = redirection
            error = http_error
            break

        # Cycle
        if url in url_stack:
            error = InfiniteRedirectsError('Infinite redirects')
            break

        redirection.status = response.status
        url_stack[url] = redirection
        location = None

        if response.status not in REDIRECT_STATUSES:

            if response.status < 400:

                if follow_refresh_header:
                    refresh = response.getheader('refresh')

                    if refresh is not None:
                        p = parse_http_refresh(refresh)

                        if p is not None:
                            location = p[1]
                            redirection.type = 'refresh-header'

                if location is None and follow_meta_refresh:
                    try:
                        response._body = response.read(1024)
                    except Exception as e:
                        error = explain_request_error(e)
                        redirection.type = 'error'
                        break

                    meta_refresh = find_meta_refresh(response._body)

                    if meta_refresh is not None:
                        location = meta_refresh[1]

                        redirection.type = 'meta-refresh'

                if location is None and follow_js_relocation:
                    try:
                        if response._body is None:
                            response._body = response.read(1024)
                    except Exception as e:
                        error = explain_request_error(e)
                        redirection.type = 'error'
                        break

                    js_relocation = find_javascript_relocation(response._body)

                    if js_relocation is not None:
                        location = js_relocation

                        redirection.type = 'js-relocation'

            # Found the end
            if location is None:
                redirection.type = 'hit'
                break
        else:
            redirection.type = 'location-header'
            location = response.getheader('location')

        # Invalid redirection
        if not location:
            error = InvalidRedirectError('Redirection is invalid')
            break

        # Location badly encoded?
        try:
            if not ASCII_RE.match(location):
                byte_location = location.encode('latin1')
                detection = chardet.detect(byte_location)
                guessed_encoding = detection['encoding'].lower()

                if (
                    guessed_encoding != 'iso-8859-1' and
                    guessed_encoding != 'ascii' and
                    detection['confidence'] >= CHARDET_CONFIDENCE_THRESHOLD
                ):
                    location = byte_location.decode(guessed_encoding)
        except:
            pass

        # Resolving next url
        next_url = urljoin(url, location.strip())

        # Self loop?
        if next_url == url:
            error = SelfRedirectError('Self redirection')
            break

        # Go to next
        url = next_url

    # We reached max redirects
    else:
        error = MaxRedirectsError('Maximum number of redirects exceeded')

    if response and not return_response:
        response.release_conn()
        response.close()

    compiled_stack = list(url_stack.values())

    if return_response:
        return error, compiled_stack, response

    return error, compiled_stack


def build_request_headers(headers=None, cookie=None, spoof_ua=False, json_body=False):

    # Formatting headers
    final_headers = {}

    if spoof_ua:
        final_headers['User-Agent'] = DEFAULT_SPOOFED_UA

    if cookie:
        if not isinstance(cookie, str):
            cookie = dict_to_cookie_string(cookie)

        final_headers['Cookie'] = cookie

    if json_body:
        final_headers['Content-Type'] = 'application/json'

    # Note: headers passed explicitly by users always win
    if headers is not None:
        final_headers.update(headers)

    return final_headers


def request(http, url, method='GET', headers=None, cookie=None, spoof_ua=True,
            follow_redirects=True, max_redirects=5, follow_refresh_header=True,
            follow_meta_refresh=False, follow_js_relocation=False, timeout=None,
            body=None, json_body=None):

    # Formatting headers
    final_headers = build_request_headers(
        headers=headers,
        cookie=cookie,
        spoof_ua=spoof_ua,
        json_body=json_body is not None
    )

    # Dealing with body
    final_body = None

    if isinstance(body, bytes):
        final_body = body
    elif isinstance(body, str):
        final_body = body.encode('utf-8')

    if json_body is not None:
        final_body = json.dumps(json_body, ensure_ascii=False).encode('utf-8')

    if not follow_redirects:
        return raw_request(
            http,
            url,
            method,
            headers=final_headers,
            body=final_body,
            timeout=timeout
        )
    else:
        err, stack, response = raw_resolve(
            http,
            url,
            method,
            headers=final_headers,
            body=final_body,
            max_redirects=max_redirects,
            return_response=True,
            follow_refresh_header=follow_refresh_header,
            follow_meta_refresh=follow_meta_refresh,
            follow_js_relocation=follow_js_relocation,
            timeout=timeout
        )

        if err:
            return err, response

        # Finishing reading body
        try:
            response._body = (response._body or b'') + response.read()
        except Exception as e:
            return explain_request_error(e), response
        finally:
            if response is not None:
                response.close()
                response.release_conn()

        return None, response


def resolve(http, url, method='GET', headers=None, cookie=None, spoof_ua=True,
            follow_redirects=True, max_redirects=5, follow_refresh_header=True,
            follow_meta_refresh=False, follow_js_relocation=False, timeout=None):

    final_headers = build_request_headers(
        headers=headers,
        cookie=cookie,
        spoof_ua=spoof_ua
    )

    return raw_resolve(
        http,
        url,
        method,
        headers=final_headers,
        max_redirects=max_redirects,
        follow_refresh_header=follow_refresh_header,
        follow_meta_refresh=follow_meta_refresh,
        follow_js_relocation=follow_js_relocation,
        timeout=timeout
    )


def extract_response_meta(response, guess_encoding=True, guess_extension=True):
    meta = {}

    # Guessing extension
    if guess_extension:

        # Guessing mime type
        mimetype, _ = mimetypes.guess_type(response.geturl())

        if mimetype is None:
            mimetype = 'text/html'

        if 'Content-Type' in response.headers:
            mimetype = response.headers['Content-Type']

        exts = mimetypes.guess_all_extensions(mimetype)

        if not exts:
            ext = '.html'
        elif '.html' in exts:
            ext = '.html'
        else:
            ext = max(exts, key=len)

        meta['mime'] = mimetype
        meta['ext'] = ext

    # Guessing encoding
    if guess_encoding:
        meta['encoding'] = guess_response_encoding(response, is_xml=True, use_chardet=True)

    return meta


def jsonrpc(http, url, method, *args, **kwargs):
    params = []

    if len(args) > 0:
        params = args
    elif len(kwargs) > 0:
        params = kwargs

    err, response = request(
        http,
        url,
        method='POST',
        json_body={
            'method': method,
            'params': params
        }
    )

    if err is not None:
        return err, None

    data = json.loads(response.data)

    return None, data


def request_json(http, url, *args, **kwargs):
    err, response = request(http, url, *args, **kwargs)

    if err:
        return err, response, None

    try:
        return None, response, json.loads(response.data.decode())
    except (JSONDecodeError, UnicodeDecodeError) as e:
        return e, response, None


def request_text(http, url, *args, encoding='utf-8', **kwargs):
    err, response = request(http, url, *args, **kwargs)

    if err:
        return err, response, None

    return None, response, response.data.decode(encoding)


class RateLimiter(object):
    """
    Naive rate limiter context manager with smooth output.

    Note that it won't work in a multi-threaded environment.

    Args:
        max_per_period (int): Maximum number of calls per period.
        period (float): Duration of a period in seconds. Defaults to 1.0.

    """

    def __init__(self, max_per_period, period=1.0, with_budget=False):
        max_per_second = max_per_period / period
        self.min_interval = 1.0 / max_per_second
        self.max_budget = period / 4
        self.budget = 0.0
        self.last_entry = None
        self.with_budget = with_budget

    def enter(self):
        self.last_entry = time.perf_counter()

    def __enter__(self):
        return self.enter()

    def exit_with_budget(self):
        running_time = time.perf_counter() - self.last_entry

        delta = self.min_interval - running_time

        # Consuming budget
        if delta >= self.budget:
            delta -= self.budget
            self.budget = 0
        else:
            self.budget -= delta
            delta = 0

        # Do we need to sleep?
        if delta > 0:
            time.sleep(delta)
        elif delta < 0:
            self.budget -= delta

        # Clamping budget
        # TODO: this should be improved by a circular buffer of last calls
        self.budget = min(self.budget, self.max_budget)

    def exit(self):
        running_time = time.perf_counter() - self.last_entry

        delta = self.min_interval - running_time

        if delta > 0:
            time.sleep(delta)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.with_budget:
            return self.exit_with_budget()

        return self.exit()


class RetryableIterator(object):
    """
    Iterator exposing a #.retry method that will make sure the next item
    is the same as the current one.
    """

    def __init__(self, iterator):
        self.iterator = iter(iterator)
        self.current_value = None
        self.retried = False
        self.retries = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.retried:
            self.retried = False
            return self.current_value

        self.retries = 0
        self.current_value = next(self.iterator)
        return self.current_value

    def retry(self):
        self.retries += 1
        self.retried = True


class RateLimitedIterator(object):
    """
    Handy iterator wrapper that will yield its items while respecting a given
    rate limit and that will not sleep needlessly when the iterator is
    finally fully consumed.
    """

    def __init__(self, iterator, max_per_period, period=1.0):
        self.iterator = RetryableIterator(iterator)
        self.rate_limiter = RateLimiter(max_per_period, period)
        self.empty = False

        try:
            self.next_value = next(self.iterator)
        except StopIteration:
            self.next_value = None
            self.empty = True

    @property
    def retries(self):
        return self.iterator.retries

    def retry(self):
        return self.iterator.retry()

    def __iter__(self):
        if self.empty:
            return

        while True:
            self.rate_limiter.enter()

            yield self.next_value

            # NOTE: if the iterator is fully consumed, this will raise StopIteration
            # and skip the exit part that could sleep needlessly
            try:
                self.next_value = next(self.iterator)
            except StopIteration:
                return

            self.rate_limiter.exit()


class RateLimiterState(object):
    def __init__(self, max_per_period, period=1.0):
        max_per_second = max_per_period / period
        self.min_interval = 1.0 / max_per_second
        self.last_entry = None

    def wait_if_needed(self):
        if self.last_entry is None:
            return

        running_time = time.perf_counter() - self.last_entry
        delta = self.min_interval - running_time

        if delta > 0:
            time.sleep(delta)

    def update(self):
        self.last_entry = time.perf_counter()


def rate_limited(max_per_period, period=1.0):
    state = RateLimiterState(max_per_period, period)

    def decorate(fn):

        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            state.wait_if_needed()
            result = fn(*args, **kwargs)
            state.update()

            return result

        return decorated

    return decorate


def rate_limited_from_state(state):
    def decorate(fn):

        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            state.wait_if_needed()
            result = fn(*args, **kwargs)
            state.update()

            return result

        return decorated

    return decorate


def rate_limited_method(attr='rate_limiter_state'):
    def decorate(fn):

        @functools.wraps(fn)
        def decorated(self, *args, **kwargs):
            state = getattr(self, attr)

            if not isinstance(state, RateLimiterState):
                raise ValueError

            state.wait_if_needed()
            result = fn(self, *args, **kwargs)
            state.update()

            return result

        return decorated

    return decorate


class PseudoFStringFormatter(string.Formatter):
    def get_field(self, field_name, args, kwargs):
        result = eval(field_name, None, kwargs)

        return result, None


def fstring_eval(template, **kwargs):
    return eval(
        'f"""%s"""' % template,
        None,
        kwargs
    )


def load_definition(f):
    string_path = isinstance(f, str)

    if string_path:
        path = f
        f = open(path)
    else:
        path = f.name

    if path.endswith('.json'):
        definition = json.load(f)

    elif path.endswith('.yml') or path.endswith('.yaml'):
        definition = yaml.load(f, Loader=yaml.Loader)

    else:
        raise TypeError('Unsupported definition file format')

    if string_path:
        f.close()

    return definition


def nested_get(path, o, default=None):
    if isinstance(path, str):
        path = path.split('.')

    for step in path:
        try:
            if callable(getattr(o, '__getitem__')):
                o = o[step]
            else:
                getattr(o, step)
        except (IndexError, KeyError, AttributeError):
            return default

    return o


def sleep_with_entropy(seconds, max_random_addendum):
    random_addendum = uniform(0, max_random_addendum)
    time.sleep(seconds + random_addendum)


def chunks_iter(iterator, chunk_size):
    chunk = []

    for item in iterator:
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []

        chunk.append(item)

    if chunk:
        yield chunk
