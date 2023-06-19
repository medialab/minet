import re
import casanova
from functools import wraps

from minet.constants import DEFAULT_SPOOFED_UA


def with_open(filename, mode):
    def decorate(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            with open(filename, mode) as file:
                return fn(file, *args, **kwargs)

        return decorated

    return decorate


@with_open("./scripts/useragents/list.csv", "r")
@with_open("./scripts/useragents/list_new.csv", "w")
@with_open("./minet/constants.py", "r+")
def update(constants, new_list, list):
    enricher = casanova.enricher(list, new_list)

    # headers
    agent = enricher.headers.agent
    used = enricher.headers.used

    written = False

    for row in enricher:
        if row[used] == "" and not written:
            print(f"print one : {row[agent]}")
            nua = row[agent]
            python = constants.read()
            new = python.replace(DEFAULT_SPOOFED_UA, nua)

            constants.truncate(0)
            constants.seek(0)
            constants.write(new)

            row[used] = True
            written = True

        enricher.writerow(row)


update()
