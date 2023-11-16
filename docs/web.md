# Minet Web Utilities

Documentation for web-related utilities exported by the `minet.web` module, such as functions able to perform one-shot http requests, resolve urls etc.

## Summary

- [request](#request)
- [resolve](#resolve)
- [Response](#response)
- [Redirection](#redirection)

## request

## resolve

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
- **soup() -> [WonderfulSoup](./soup.md#wonderfulsoup)**: method parsing the response's text as HTML and returning a soup useful for scraping etc.
- **links() -> List[str]**: method extracting links from the response's html body by finding `<a>` tags containing relevant urls.

## Redirection

Class representing a single step in a redirection stack, as returned by the [resolve](#resolve) function.

*Attributes*

- **url** *str*: url of the redirection.
- **type** *str*: the type of redirection. Must be one of `hit`, `location-header`, `js-relocation`, `refresh-header`, `meta-refresh`, `infer` or `canonical`.
- **status** *Optional[int]*: status of the related HTTP response, if applicable (e.g. if the redirection type is `infer`, `status` will be `None`).
