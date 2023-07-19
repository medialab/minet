# =============================================================================
# Minet Headers Utils
# =============================================================================
#
# Miscellaneous functions related to HTTP headers.
#
from typing import Optional, Tuple

import cgi


def parse_http_header(header: str) -> Tuple[str, str]:
    key, value = header.split(":", 1)

    return key.strip(), value.strip()


def get_encoding_from_content_type_header(
    content_type_header: Optional[str],
) -> Optional[str]:
    if content_type_header is None:
        return None

    parsed_header = cgi.parse_header(content_type_header)

    if len(parsed_header) > 1:
        charset = parsed_header[1].get("charset")

        if charset is not None:
            return charset.lower()

    return None


# TODO: take more cases into account...
#   http://www.otsukare.info/2015/03/26/refresh-http-header
def parse_http_refresh(value) -> Optional[Tuple[int, str]]:
    try:
        if isinstance(value, bytes):
            value = value.decode()

        duration, url = value.strip().split(";", 1)

        if not url.lower().strip().startswith("url="):
            return None

        return int(duration), str(url.split("=", 1)[1])
    except Exception:
        return None
