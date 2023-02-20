import time
import sys
from random import random

from minet.cli.loading_bar import LoadingBar


N = 10
SUB_N = 1_000

NESTED = True

try:
    with LoadingBar(
        title="Processing",
        total=None,
        unit="apples",
        sub_unit="pears",
        stats=[
            {"name": "errors", "style": "error"},
            {"name": "warnings", "style": "warning"},
        ],
        nested=NESTED,
    ) as loading_bar:

        if not NESTED:
            for i in range(SUB_N):
                time.sleep(0.005)
                loading_bar.advance()

        else:
            for i in range(N):
                with loading_bar.nested_task("Working on [info]%i[/info]" % i):
                    for j in range(SUB_N):
                        time.sleep(0.001)
                        loading_bar.nested_advance()

                        if random() < 0.001:
                            loading_bar.inc_stat("errors")

                        if random() < 0.005:
                            loading_bar.inc_stat("warnings")

except KeyboardInterrupt:
    sys.exit(1)
