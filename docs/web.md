# Minet Web Utilities

Documentation for web-related utilities exported by the `minet.web` module, such as functions able to perform one-shot http requests, resolve urls etc.

## Summary

- [request](#request)
- [resolve](#resolve)
- [Response](#response)
- [Redirection](#redirection)

## request

Perform a single HTTP request and return the completed [Response](#response) object. This function will only raise if something prevented the HTTP request to complete (e.g. network is down, target host does not exists etc.) but not if the resulting response has a non-200 HTTP status (unless the `raise_on_statuses` kwarg is given).

*Examples*

```python
from minet.web import request

# Basic GET call
response = request("https://www.lemonde.fr/")
print(response.status, len(response))

# POST request with custom headers and JSON body
response = request(
  "https://www.lemonde.fr/",
  method="POST",
  headers={"User-Agent": "Minet/1.1.7"},
  json_body={"id": "3463"}
)
```

*Arguments*

- **url** *str*: url to request.
- **method** *Optional[str]* [`GET`]: HTTP method to use.
- **headers** *Optional[dict[str, str]]*: HTTP headers, as a dict, to use for the request.
- **cookie** *Optional[str | dict[str, str]]*: cookie string to pass as the `Cookie` header value. Can also be a cookie morsel dict mapping names to their values.
- **spoof_ua** *bool* [`False`]: whether to use a plausible `User-Agent` header when performing the query.
- **follow_redirects** *bool* [`True`]: whether to allow the request to follow redirections.
- **max_redirects** *int* [`5`]: maximum number of redirections the request will be allowed to follow before raising an error.
- **follow_refresh_header** *bool* [`True`]: whether to allow the request to follow non-standard `Refresh` header redirections.
- **follow_meta_refresh** *bool* [`False`]: whether to allow the request to sniff the response body to find a `<meta>` tag containing non-standard redirection information.
- **follow_js_relocation** *bool* [`False`]: whether to allow the request to sniff the response body to find typical patterns of JavaScript url relocation.
- **infer_redirection** *bool* [`False`]: whether to use [`ural.infer_redirection`](https://github.com/medialab/ural#infer_redirection) to allow redirection inference directly from analyzing the traversed urls.
- **canonicalize** *bool* [`False`]: whether to allow the request to sniff the response body to find a different canonical url in the a relevant `<link>` tag and push it as a virtual redirection in the stack.
- **known_encoding** *Optional[str]* [`utf-8`]: encoding of the response's text, if known beforehand. Set `known_encoding` to `None` if you want the request to infer the response's encoding.
- **timeout** *Optional[float | urllib3.Timeout]*: timeout in seconds before raising an error.
- **body** *Optional[str | bytes]*: body of the request as a string or raw bytes.
- **json_body** *Optional[Any]*: data to serialize as JSON and to be sent as the request's body.
- **urlencoded_body** *Optional[dict[str, str | int | float]]*: dict to serialize as a key-value urlencoded body to be sent with the request.
- **cancel_event** *Optional[threading.Event]*: threading event that will be used to assess whether the request should be cancelled while we are still downloading its response's body.
- **raise_on_statuses** *Optional[Container[int]]*: if given, request will raise if the response has a status in the given set, instead of returning the response.
- **stateful** *bool* [`False`]: whether to allow the resolver to be stateful and store cookies along the redirection chain. This is useful when dealing with GDPR compliance patterns from websites etc. but can hurt performance a little bit.
- **use_pycurl** *bool* [`False`]: whether to use [`pycurl`](http://pycurl.io/) instead of [`urllib3`](https://urllib3.readthedocs.io/en/stable/) to perform the request. The `pycurl` library must be installed for this kwarg to work.
- **compressed** *bool* [`False`]: whether to automatically specifiy the `Accept` header to ask the server to compress the response's body on the wire.
- **pool_manager** *Optional[urllib3.PoolManager]*: urllib3 pool manager to use to perform the request. Will use a default sensible pool manager if not given. This should only be cared about when you want to use a custom pool manager. This will not be used if `pycurl=True`.

## resolve

Resolve the given url by following its redirections and return the full redirection chain as a list of [Redirection](#redirection) objects. This function may raise when the maximum number of redirections is exceeded, if some relocation is invalid or if we end up in an infinite cycle.

*Examples*

```python
from minet.web import resolve

# Basic GET call
redirections = resolve("https://www.lemonde.fr/")
print('Resolved url:', redirections[-1].url)

# Overcome some GDPR compliance issues related to cookies
redirections = resolve("https://www.lemonde.fr/", stateful=True)
```

*Arguments*

- **url** *str*: url to request.
- **headers** *Optional[dict[str, str]]*: HTTP headers, as a dict, to use for the request.
- **cookie** *Optional[str | dict[str, str]]*: cookie string to pass as the `Cookie` header value. Can also be a cookie morsel dict mapping names to their values.
- **spoof_ua** *bool* [`False`]: whether to use a plausible `User-Agent` header when performing the query.
- **max_redirects** *int* [`5`]: maximum number of redirections the request will be allowed to follow before raising an error.
- **follow_refresh_header** *bool* [`True`]: whether to allow the request to follow non-standard `Refresh` header redirections.
- **follow_meta_refresh** *bool* [`False`]: whether to allow the request to sniff the response body to find a `<meta>` tag containing non-standard redirection information.
- **follow_js_relocation** *bool* [`False`]: whether to allow the request to sniff the response body to find typical patterns of JavaScript url relocation.
- **infer_redirection** *bool* [`False`]: whether to use [`ural.infer_redirection`](https://github.com/medialab/ural#infer_redirection) to allow redirection inference directly from analyzing the traversed urls.
- **canonicalize** *bool* [`False`]: whether to allow the request to sniff the response body to find a different canonical url in the a relevant `<link>` tag and push it as a virtual redirection in the stack.
- **timeout** *Optional[float | urllib3.Timeout]*: timeout in seconds before raising an error.
- **cancel_event** *Optional[threading.Event]*: threading event that will be used to assess whether the request should be cancelled while we are still downloading its response's body.
- **raise_on_statuses** *Optional[Container[int]]*: if given, request will raise if the response has a status in the given set, instead of returning the response.
- **stateful** *bool* [`False`]: whether to allow the resolver to be stateful and store cookies along the redirection chain. This is useful when dealing with GDPR compliance patterns from websites etc. but can hurt performance a little bit.
- **pool_manager** *Optional[urllib3.PoolManager]*: urllib3 pool manager to use to perform the request. Will use a default sensible pool manager if not given. This should only be cared about when you want to use a custom pool manager.

## Response

Class representing a completed HTTP response (that is to say the body was fully downloaded).

*Attributes*

- **url** *str*: requested url (before any redirection).
- **start_url** *str*: alias for `response.url`.
- **end_url** *str*: last reached url (after redirection). Shorthand for `response.stack[-1].url`.
- **status** *int*: HTTP status for the response, e.g. `200`, `404`.
- **headers** *urllib3.HTTPHeaderDict*: dict of the response's headers.
- **body** *bytes*: content of the response.
- **stack** *list[[Redirection](#redirection)]*: redirection stack of the response.
- **was_redirected** *bool*: whether the response followed at least one redirection or not.
- **end_datetime** *datetime*: time when the response finally completed.
- **ext** *Optional[str]*: plausible extension for the kind of file retrieved by the response, e.g. `.html`, `.pdf` etc.
- **mimetype** *Optional[str]*: mimetype of the response, inferred from the headers, the url and sometimes by sniffing the content (usually for html).
- **is_text** *bool*: whether the response's body is inferred to be text. Reverse of `response.is_binary`.
- **is_binary** *bool*: whether the response's body is inferred to be binary. Reverse of `response.is_text`.
- **could_be_html** *bool*: whether the response could be html (inferred from headers and mimetype).
- **is_html** *bool*: whether the response actually is html (inferred from sniffing the body).
- **encoding** *Optional[str]*: encoding of the response, as inferred from headers, html patterns and/or sniffing the body. Will be `None` if response body is deemed to be binary.
- **likely_encoding** *str*: likely encoding of the response, defaulting to `utf-8`, even when the response body is deemed to be binary.
- **encoding_from_headers** *Optional[str]*: encoding of the response, according to its headers.
- **human_size** *str*: formatted and human-readable size of the response body in bytes.

*Methods*

- **urljoin(target: str) -> str**: shorthand for `urllib.parse.urljoin(response.end_url, target)`.
- **text() -> str**: method returning the decoded (as per inferred or known encoding) body of the response as text.
- **json() -> Any**: method parsing the response's text as JSON.
- **soup() -> [WonderfulSoup](./soup.md)**: method parsing the response's text as HTML and returning a soup useful for scraping etc.
- **links() -> List[str]**: method extracting links from the response's html body by finding `<a>` tags containing relevant urls.

## Redirection

Class representing a single step in a redirection stack, as returned by the [resolve](#resolve) function.

*Attributes*

- **url** *str*: url of the redirection.
- **type** *str*: the type of redirection. Must be one of `hit`, `location-header`, `js-relocation`, `refresh-header`, `meta-refresh`, `infer` or `canonical`.
- **status** *Optional[int]*: status of the related HTTP response, if applicable (e.g. if the redirection type is `infer`, `status` will be `None`).
