import warnings
from contextlib import contextmanager

try:
    from bs4 import XMLParsedAsHTMLWarning
except ImportError:
    XMLParsedAsHTMLWarning = None


@contextmanager
def suppress_xml_parsed_as_html_warnings(bypass=False):
    try:
        if XMLParsedAsHTMLWarning is None or bypass:
            yield
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=XMLParsedAsHTMLWarning)
                yield
    finally:
        pass
