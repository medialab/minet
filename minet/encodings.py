# =============================================================================
# Minet Encodings
# =============================================================================
#
# List of python-supported encodings so we can ensure we will be able to
# correctly handle them.
#
from typing import Optional

import re
import charset_normalizer

ENCODINGS = set(
    [
        "1125",
        "273",
        "437",
        "646",
        "850",
        "852",
        "855",
        "857",
        "858",
        "860",
        "861",
        "862",
        "863",
        "865",
        "866",
        "869",
        "8859",
        "932",
        "936",
        "949",
        "950",
        "arabic",
        "ascii",
        "big5",
        "big5hkscs",
        "big5tw",
        "chinese",
        "cp037",
        "cp1006",
        "cp1026",
        "cp1125",
        "cp1140",
        "cp1250",
        "cp1251",
        "cp1252",
        "cp1253",
        "cp1254",
        "cp1255",
        "cp1256",
        "cp1257",
        "cp1258",
        "cp1361",
        "cp154",
        "cp273",
        "cp424",
        "cp437",
        "cp500",
        "cp65001",
        "cp720",
        "cp737",
        "cp775",
        "cp819",
        "cp850",
        "cp852",
        "cp855",
        "cp856",
        "cp857",
        "cp858",
        "cp860",
        "cp861",
        "cp862",
        "cp863",
        "cp864",
        "cp865",
        "cp866",
        "cp866u",
        "cp869",
        "cp874",
        "cp875",
        "cp932",
        "cp936",
        "cp949",
        "cp950",
        "cpgr",
        "cpis",
        "csbig5",
        "csibm273",
        "csiso2022jp",
        "csiso2022kr",
        "csiso58gb231280",
        "csptcp154",
        "csshiftjis",
        "cyrillic",
        "cyrillicasian",
        "ebcdiccpbe",
        "ebcdiccpch",
        "ebcdiccphe",
        "euccn",
        "eucgb2312cn",
        "eucjis2004",
        "eucjisx0213",
        "eucjp",
        "euckr",
        "gb18030",
        "gb180302000",
        "gb2312",
        "gb23121980",
        "gb231280",
        "gbk",
        "greek",
        "greek8",
        "hebrew",
        "hkscs",
        "hz",
        "hzgb",
        "hzgb2312",
        "ibm037",
        "ibm039",
        "ibm1026",
        "ibm1125",
        "ibm1140",
        "ibm273",
        "ibm424",
        "ibm437",
        "ibm500",
        "ibm775",
        "ibm850",
        "ibm852",
        "ibm855",
        "ibm857",
        "ibm858",
        "ibm860",
        "ibm861",
        "ibm862",
        "ibm863",
        "ibm864",
        "ibm865",
        "ibm866",
        "ibm869",
        "iso2022jp",
        "iso2022jp1",
        "iso2022jp2",
        "iso2022jp2004",
        "iso2022jp3",
        "iso2022jpext",
        "iso2022kr",
        "iso88591",
        "iso885910",
        "iso885911",
        "iso885913",
        "iso885914",
        "iso885915",
        "iso885916",
        "iso88592",
        "iso88593",
        "iso88594",
        "iso88595",
        "iso88596",
        "iso88597",
        "iso88598",
        "iso88599",
        "isoir58",
        "jisx0213",
        "johab",
        "koi8r",
        "koi8u",
        "korean",
        "ksc5601",
        "ksc56011987",
        "ksx1001",
        "l1",
        "l10",
        "l2",
        "l3",
        "l4",
        "l5",
        "l6",
        "l7",
        "l8",
        "l9",
        "latin",
        "latin1",
        "latin10",
        "latin2",
        "latin3",
        "latin4",
        "latin5",
        "latin6",
        "latin7",
        "latin8",
        "latin9",
        "maccentraleurope",
        "maccyrillic",
        "macgreek",
        "maciceland",
        "macintosh",
        "maclatin2",
        "macroman",
        "macturkish",
        "ms1361",
        "ms932",
        "ms936",
        "ms949",
        "ms950",
        "mskanji",
        "pt154",
        "ptcp154",
        "ruscii",
        "shiftjis",
        "shiftjis2004",
        "shiftjisx0213",
        "sjis",
        "sjis2004",
        "sjisx0213",
        "thai",
        "u16",
        "u32",
        "u7",
        "u8",
        "uhc",
        "ujis",
        "unicode11utf7",
        "usascii",
        "utf",
        "utf16",
        "utf16be",
        "utf16le",
        "utf32",
        "utf32be",
        "utf32le",
        "utf7",
        "utf8",
        "utf8sig",
        "windows1250",
        "windows1251",
        "windows1252",
        "windows1253",
        "windows1254",
        "windows1255",
        "windows1256",
        "windows1257",
        "windows1258",
    ]
)

CLEANER_RE = re.compile(r"[\s\-_]")


def normalize_encoding(encoding: str) -> str:
    return re.sub(CLEANER_RE, "", encoding).lower()


def is_supported_encoding(encoding):
    return normalize_encoding(encoding) in ENCODINGS


def encoding_sort_key(encoding):
    return (normalize_encoding(encoding), -len(encoding))


def infer_charset(
    data: bytes, only_supported_encodings: bool = True
) -> Optional[charset_normalizer.CharsetMatch]:
    matches = charset_normalizer.from_bytes(data)

    for match in matches:
        if not only_supported_encodings or is_supported_encoding(match.encoding):
            return match

    return None


def infer_encoding(data: bytes, only_supported_encodings: bool = True) -> Optional[str]:
    charset = infer_charset(data, only_supported_encodings=only_supported_encodings)

    if charset is None:
        return None

    return charset.encoding


UTF8_BOM = b"\xef\xbb\xbf"
UTF16_LE_BOM = b"\xff\xfe"
UTF16_BE_BOM = b"\xfe\xff"
UTF32_LE_BOM = b"\xff\xfe\x00\x00"
UTF32_BE_BOM = b"\x00\x00\xfe\xff"


def fix_surrogates(string: str) -> str:
    try:
        return string.encode("utf-16", errors="surrogatepass").decode("utf-16")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return string.encode("utf-8", errors="replace").decode("utf-8")
