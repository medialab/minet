import pycurl
import certifi
from io import BytesIO
from dataclasses import dataclass
from ebbe import format_repr, format_filesize


try:
    from urllib3 import HTTPHeaderDict
except ImportError:
    from urllib3._collections import HTTPHeaderDict


@dataclass
class PycurlResult:
    url: str
    body: bytes
    headers: HTTPHeaderDict
    status: int

    def __repr__(self) -> str:
        return format_repr(
            self, ["url", "status", ("size", format_filesize(len(self.body)))]
        )


def request_with_pycurl(
    url: str,
    follow_redirects: bool = True,
) -> PycurlResult:
    curl = pycurl.Curl()
    buffer = BytesIO()

    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, buffer)
    curl.setopt(pycurl.CAINFO, certifi.where())

    headers = HTTPHeaderDict()

    def header_function(header_line):
        header_line = header_line.decode("iso-8859-1")

        if ":" not in header_line:
            return

        name, value = header_line.split(":", 1)

        name = name.strip()
        value = value.strip()

        headers[name] = value

    curl.setopt(pycurl.HEADERFUNCTION, header_function)

    if follow_redirects:
        curl.setopt(pycurl.FOLLOWLOCATION, True)

    curl.perform()

    status = curl.getinfo(pycurl.HTTP_CODE)

    curl.close()

    return PycurlResult(url=url, body=buffer.getvalue(), headers=headers, status=status)
