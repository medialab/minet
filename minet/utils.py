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
import urllib3
import json
import yaml
import time
import string
import mimetypes
import cchardet as chardet
from collections import OrderedDict
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

from minet.defaults import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_READ_TIMEOUT,
    DEFAULT_SPOOFED_UA
)

# Fix for pyinstaller. Do not remove!
import encodings.idna

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

# Constants
CHARDET_CONFIDENCE_THRESHOLD = 0.9
REDIRECT_STATUSES = set(HTTPResponse.REDIRECT_STATUSES)


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

        if not url.lower().startswith('url='):
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
    if browser == 'firefox':
        try:
            return CookieResolver(browser_cookie3.firefox())
        except:
            return None

    if browser == 'chrome':
        try:
            return CookieResolver(browser_cookie3.chrome())
        except:
            return None

    raise Exception('minet.utils.grab_cookies: unknown "%s" browser.' % browser)


def dict_to_cookie_string(d):
    return '; '.join('%s=%s' % r for r in d.items())


DEFAULT_URLLIB3_TIMEOUT = urllib3.Timeout(connect=DEFAULT_CONNECT_TIMEOUT, read=DEFAULT_READ_TIMEOUT)


def create_pool(proxy=None, threads=None, **kwargs):
    """
    Helper function returning a urllib3 pool manager with sane defaults.
    """

    manager_kwargs = {
        'cert_reqs': 'CERT_REQUIRED',
        'ca_certs': certifi.where(),
        'timeout': DEFAULT_URLLIB3_TIMEOUT
    }

    manager_kwargs.update(kwargs)

    if threads is not None:

        # TODO: maxsize should increase with group_parallelism
        manager_kwargs['maxsize'] = 1
        manager_kwargs['num_pools'] = threads * 2

    if proxy is not None:
        return urllib3.ProxyManager(proxy, **manager_kwargs)

    return urllib3.PoolManager(**manager_kwargs)


def explain_request_error(error):
    return error


def raw_request(http, url, method='GET', headers=None,
                preload_content=True, release_conn=True):
    """
    Generic request helpers using a urllib3 pool to access some resource.
    """

    # Validating URL
    if not is_url(url, require_protocol=True, tld_aware=True, allow_spaces_in_path=True):
        return InvalidURLError('Invalid URL'), None

    # Performing request
    try:
        response = http.request(
            method,
            url,
            headers=headers,
            preload_content=preload_content,
            release_conn=release_conn,
            redirect=False,
            retries=False
        )
    except Exception as e:
        return explain_request_error(e), None

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
                follow_js_relocation=False, return_response=False):
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
            preload_content=False,
            release_conn=False
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


def build_request_headers(headers=None, cookie=None, spoof_ua=False):

    # Formatting headers
    final_headers = {}

    if spoof_ua:
        final_headers['User-Agent'] = DEFAULT_SPOOFED_UA

    if cookie:
        if not isinstance(cookie, str):
            cookie = dict_to_cookie_string(cookie)

        final_headers['Cookie'] = cookie

    # Note: headers passed explicitly by users always win
    if headers is not None:
        final_headers.update(headers)

    return final_headers


def request(http, url, method='GET', headers=None, cookie=None, spoof_ua=True,
            follow_redirects=True, max_redirects=5, follow_refresh_header=True,
            follow_meta_refresh=False, follow_js_relocation=False):

    # Formatting headers
    final_headers = build_request_headers(headers=headers, cookie=cookie, spoof_ua=spoof_ua)

    if not follow_redirects:
        return raw_request(
            http,
            url,
            method,
            headers=final_headers
        )
    else:
        err, stack, response = raw_resolve(
            http,
            url,
            method,
            headers=final_headers,
            max_redirects=max_redirects,
            return_response=True,
            follow_refresh_header=follow_refresh_header,
            follow_meta_refresh=follow_meta_refresh,
            follow_js_relocation=follow_js_relocation
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
            follow_meta_refresh=False, follow_js_relocation=False):

    final_headers = build_request_headers(headers=headers, cookie=cookie, spoof_ua=spoof_ua)

    return raw_resolve(
        http,
        url,
        method,
        headers=final_headers,
        max_redirects=max_redirects,
        follow_refresh_header=follow_refresh_header,
        follow_meta_refresh=follow_meta_refresh,
        follow_js_relocation=follow_js_relocation
    )


def extract_response_meta(response, guess_encoding=True, guess_extension=True):
    meta = {}

    # Guessing mime type
    mimetype, _ = mimetypes.guess_type(response.geturl())

    if mimetype is None:
        mimetype = 'text/html'

    # Guessing extension
    # TODO: maybe move to utils
    if guess_extension:
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


class RateLimiter(object):
    """
    Naive rate limiter context manager with smooth output ().

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

    def __enter__(self):
        self.last_entry = time.perf_counter()

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
