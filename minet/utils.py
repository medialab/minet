# =============================================================================
# Minet Utils
# =============================================================================
#
# Miscellaneous helper function used throughout the library.
#
import re
import chardet
import cgi

# Handy regexes
CHARSET_RE = re.compile(rb'<meta.*?charset=["\']*(.+?)["\'>]', flags=re.I)
PRAGMA_RE = re.compile(rb'<meta.*?content=["\']*;?charset=(.+?)["\'>]', flags=re.I)
XML_RE = re.compile(rb'^<\?xml.*?encoding=["\']*(.+?)["\'>]')

# Constants
CHARDET_CONFIDENCE_THRESHOLD = 0.9


def guess_encoding(response, data, is_xml=False, use_chardet=False):
    """
    Function taking an urllib3 response object and attempting to guess its
    encoding.
    """
    content_type_header = response.getheader('content-type')

    if content_type_header is not None:
        parsed_header = cgi.parse_header(content_type_header)

        if len(parsed_header) > 1:
            charset = parsed_header[1].get('charset')

            if charset is not None:
                return charset.lower()

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
            return matches[-1].lower().decode()

    if use_chardet:
        chardet_result = chardet.detect(data)

        if chardet_result['confidence'] >= CHARDET_CONFIDENCE_THRESHOLD:
            return chardet_result['encoding'].lower()

    return None
