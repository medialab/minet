# =============================================================================
# Minet Regex Scrapers
# =============================================================================
#
# Handful of "scrapers" able to extract information from HTML without parsing
# anything with handy regexes.
#
# Those are also typically able to work on raw bytes so one does not need to
# even decode the HTML.
#
from typing import Optional, Dict, List

import re
from itertools import chain
from collections import defaultdict
from ural import urls_from_html, canonicalize_url, should_follow_href, is_url
from urllib.parse import urljoin

from minet.encodings import normalize_encoding
from minet.headers import parse_http_refresh

CHARSET_RE = re.compile(rb'<meta.*?charset=["\']*(.+?)["\'>]', flags=re.I)
PRAGMA_RE = re.compile(rb'<meta.*?content=["\']*;?charset=(.+?)["\'>]', flags=re.I)
XML_RE = re.compile(rb'^\s*<\?xml.*?encoding=["\']*(.+?)["\'>]', flags=re.I)


def extract_encodings_from_xml(
    body: bytes, chunk_size: Optional[int] = 1024
) -> Dict[str, int]:
    possibilities = defaultdict(list)

    chunk = body

    if chunk_size is not None:
        chunk = body[:chunk_size]

    matches = chain(
        re.findall(CHARSET_RE, chunk),
        re.findall(PRAGMA_RE, chunk),
        re.findall(XML_RE, chunk),
    )

    for match in matches:
        encoding = match.decode().lower()
        possibilities[normalize_encoding(encoding)].append(encoding)

    return {max(names, key=len): len(names) for names in possibilities.values()}


HREF_RE = re.compile(rb'href=(\"[^"]+|\'[^\']+|[^\s]+)>?\s?', flags=re.I)


def extract_href(value):
    m = HREF_RE.search(value)

    if not m:
        return None

    url = m.group(1)

    try:
        url = url.decode("utf-8")
    except UnicodeDecodeError:
        return None

    return url.strip("\"'") or None


CANONICAL_LINK_RE = re.compile(
    rb'<link\s*[^>]*\s+rel=(?:"\s*canonical\s*"|canonical|\'\s*canonical\s*\')\s+[^>]*\s?/?>'
)


def extract_canonical_link(html_chunk: bytes):
    m = CANONICAL_LINK_RE.search(html_chunk)

    if not m:
        return None

    return extract_href(m.group())


JAVASCRIPT_LOCATION_RE = re.compile(
    rb"""(?:window\.)?location(?:\s*=\s*|\.replace\(\s*)['"`](.*?)['"`]"""
)
ESCAPED_SLASH_RE = re.compile(rb"\\\/")


def extract_javascript_relocation(html_chunk: bytes):
    m = JAVASCRIPT_LOCATION_RE.search(html_chunk)

    if not m:
        return None

    try:
        return ESCAPED_SLASH_RE.sub(b"/", m.group(1)).decode()
    except Exception:
        return None


META_REFRESH_RE = re.compile(
    rb"""<meta\s+http-equiv=['"]?refresh['"]?\s+content=['"]?([^"']+)['">]?""",
    flags=re.I,
)


def extract_meta_refresh(html_chunk: bytes):
    m = META_REFRESH_RE.search(html_chunk)

    if not m:
        return None

    return parse_http_refresh(m.group(1))


def extract_links(
    html_body: bytes,
    base_url: str,
    encoding: str = "utf-8",
    canonicalize: bool = False,
    unique: bool = False,
    strip_fragment: bool = False,
) -> List[str]:
    links = []
    already_seen = set()

    if canonicalize:
        base_url = canonicalize_url(base_url, strip_fragment=strip_fragment)

    for url in urls_from_html(html_body, encoding=encoding, errors="replace"):
        if not should_follow_href(url):
            continue

        url = urljoin(base_url, url)

        if not is_url(
            url,
            require_protocol=True,
            tld_aware=True,
            allow_spaces_in_path=True,
            only_http_https=True,
        ):
            continue

        if canonicalize:
            url = canonicalize_url(url, strip_fragment=strip_fragment)

        if url == base_url:
            continue

        if unique:
            if url in already_seen:
                continue

            already_seen.add(url)

        links.append(url)

    return links
