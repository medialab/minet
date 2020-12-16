import fileinput
from trafilatura.core import bare_extraction
from pprint import pprint

with fileinput.input() as f:
    html = ''.join(f)

    # https://trafilatura.readthedocs.io/en/latest/corefunctions.html
    raw_content = bare_extraction(
        html
    )

    pprint(raw_content)
