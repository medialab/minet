# =============================================================================
# Minet Web Utilities
# =============================================================================
#
# Miscellaneous web-related functions used throughout the library.
#
import re
import cgi
import certifi
import browser_cookie3
import urllib3
import ural
import json
import mimetypes
import cchardet as chardet
from collections import OrderedDict
from json.decoder import JSONDecodeError
from urllib.parse import urljoin
from urllib3 import HTTPResponse
from urllib.request import Request
from urllib.error import URLError
from tenacity import (
    Retrying,
    wait_random_exponential,
    retry_if_exception_type,
    stop_after_attempt
)

from minet.encodings import is_supported_encoding
from minet.utils import is_binary_mimetype
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
HTML_RE = re.compile(rb'^<(?:html|head|body|title|meta|link|span|div|img|ul|ol|[ap!?])', flags=re.I)

# Constants
CHARDET_CONFIDENCE_THRESHOLD = 0.9
REDIRECT_STATUSES = set(HTTPResponse.REDIRECT_STATUSES)
CONTENT_CHUNK_SIZE = 1024


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
    chunk = data[:CONTENT_CHUNK_SIZE]

    # Data is empty
    if not chunk.strip():
        return None

    # TODO: use re.search to go faster!
    if is_xml:
        matches = re.findall(CHARSET_RE, chunk)

        if len(matches) == 0:
            matches = re.findall(PRAGMA_RE, chunk)

        if len(matches) == 0:
            matches = re.findall(XML_RE, chunk)

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


def looks_like_html(html_chunk):
    return HTML_RE.match(html_chunk) is not None


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
        manager_kwargs['maxsize'] = 10
        manager_kwargs['num_pools'] = threads * 2

    manager_kwargs.update(kwargs)

    if proxy is not None:
        return urllib3.ProxyManager(proxy, **manager_kwargs)

    return urllib3.PoolManager(**manager_kwargs)


DEFAULT_POOL = create_pool(maxsize=10, num_pools=10)


def raw_request(http, url, method='GET', headers=None,
                preload_content=True, release_conn=True, timeout=None,
                body=None):
    """
    Generic request helpers using a urllib3 pool to access some resource.
    """

    # Validating URL
    if not ural.is_url(url, require_protocol=True, tld_aware=True, allow_spaces_in_path=True):
        return InvalidURLError(url=url), None

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

    def __init__(self, url, _type='hit'):
        self.status = None
        self.url = url
        self.type = _type

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
                follow_js_relocation=False, return_response=False,
                infer_redirection=False, timeout=None, body=None,):
    """
    Helper function attempting to resolve the given url.
    """

    url_stack = OrderedDict()
    error = None
    response = None

    for _ in range(max_redirects):
        if infer_redirection:
            target = ural.infer_redirection(url, recursive=False)

            if target != url:
                url_stack[url] = Redirection(url, 'infer')
                url = target
                continue

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

                # Reading a small chunk of the html
                if location is None and (follow_meta_refresh or follow_js_relocation):
                    try:
                        response._body = response.read(CONTENT_CHUNK_SIZE)
                    except Exception as e:
                        error = e
                        redirection.type = 'error'
                        break

                # Meta refresh
                if location is None and follow_meta_refresh:
                    meta_refresh = find_meta_refresh(response._body)

                    if meta_refresh is not None:
                        location = meta_refresh[1]
                        redirection.type = 'meta-refresh'

                # JavaScript relocation
                if location is None and follow_js_relocation:
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


def request(url, pool=DEFAULT_POOL, method='GET', headers=None, cookie=None, spoof_ua=True,
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
            pool,
            url,
            method,
            headers=final_headers,
            body=final_body,
            timeout=timeout
        )
    else:
        err, _, response = raw_resolve(
            pool,
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
            return e, response
        finally:
            if response is not None:
                response.close()
                response.release_conn()

        return None, response


def resolve(url, pool=DEFAULT_POOL, method='GET', headers=None, cookie=None, spoof_ua=True,
            max_redirects=5, follow_refresh_header=True,
            follow_meta_refresh=False, follow_js_relocation=False,
            infer_redirection=False, timeout=None):

    final_headers = build_request_headers(
        headers=headers,
        cookie=cookie,
        spoof_ua=spoof_ua
    )

    return raw_resolve(
        pool,
        url,
        method,
        headers=final_headers,
        max_redirects=max_redirects,
        follow_refresh_header=follow_refresh_header,
        follow_meta_refresh=follow_meta_refresh,
        follow_js_relocation=follow_js_relocation,
        infer_redirection=infer_redirection,
        timeout=timeout
    )


def extract_response_meta(response, guess_encoding=True, guess_extension=True):
    meta = {
        'ext': None,
        'mimetype': None,
        'encoding': None,
        'is_text': None
    }

    # Guessing extension
    if guess_extension:

        # Guessing mime type
        # TODO: validate mime type string?
        mimetype, _ = mimetypes.guess_type(response.geturl())

        if 'Content-Type' in response.headers:
            content_type = response.headers['Content-Type']
            parsed_header = cgi.parse_header(content_type)

            if parsed_header and parsed_header[0].strip():
                mimetype = parsed_header[0].strip()

        if mimetype is None and looks_like_html(response.data[:CONTENT_CHUNK_SIZE]):
            mimetype = 'text/html'

        if mimetype is not None:
            ext = mimetypes.guess_extension(mimetype)

            if ext == '.htm':
                ext = '.html'
            elif ext == '.jpe':
                ext = '.jpg'

            meta['mimetype'] = mimetype
            meta['ext'] = ext

    if meta['mimetype'] is not None:
        meta['is_text'] = not is_binary_mimetype(meta['mimetype'])

        if not meta['is_text']:
            guess_encoding = False

    # Guessing encoding
    if guess_encoding:
        meta['encoding'] = guess_response_encoding(response, is_xml=True, use_chardet=True)

    return meta


def request_jsonrpc(url, method, pool=DEFAULT_POOL, *args, **kwargs):
    params = []

    if len(args) > 0:
        params = args
    elif len(kwargs) > 0:
        params = kwargs

    err, response = request(
        url,
        pool=pool,
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


def request_json(url, pool=DEFAULT_POOL, *args, **kwargs):
    err, response = request(url, pool=pool, *args, **kwargs)

    if err:
        return err, response, None

    try:
        return None, response, json.loads(response.data.decode())
    except (JSONDecodeError, UnicodeDecodeError) as e:
        return e, response, None


def request_text(url, pool=DEFAULT_POOL, *args, encoding='utf-8', **kwargs):
    err, response = request(url, pool=pool, *args, **kwargs)

    if err:
        return err, response, None

    return None, response, response.data.decode(encoding)


THREE_HOURS = 3 * 60 * 60


def create_request_retryer(min=10, max=THREE_HOURS, max_attempts=9, before_sleep=None,
                           additional_exceptions=None):

    retry_for = [
        urllib3.exceptions.TimeoutError,
        URLError  # NOTE: attempting this to see if it does not cause issues
    ]

    if additional_exceptions:
        for exc in additional_exceptions:
            retry_for.append(exc)

    return Retrying(
        wait=wait_random_exponential(exp_base=6, min=min, max=max),
        retry=retry_if_exception_type(
            exception_types=tuple(retry_for)
        ),
        stop=stop_after_attempt(max_attempts),
        before_sleep=before_sleep if callable(before_sleep) else None
    )
