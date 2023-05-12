import time
import sys
import argparse
from random import random

from minet.cli.loading_bar import LoadingBar

parser = argparse.ArgumentParser()
parser.add_argument("--unknown", action="store_true", default=False)
parser.add_argument("--nested", action="store_true", default=False)

cli_args = parser.parse_args()

N = 10
SUB_N = 1_000
UNKNOWN = cli_args.unknown
NESTED = cli_args.nested

try:
    with LoadingBar(
        title="Processing",
        total=None if UNKNOWN else (N if NESTED else SUB_N),
        unit="apples",
        sub_unit="pears",
        stats=[
            {"name": "errors", "style": "error"},
            {"name": "warnings", "style": "warning"},
        ],
        nested=NESTED,
        sub_title_style="",
    ) as loading_bar:
        if not NESTED:
            for i in range(SUB_N):
                time.sleep(0.005)
                loading_bar.advance()

        else:
            for i in range(N):
                with loading_bar.step(
                    "Working on [info]%i[/info]" % i, sub_total=SUB_N
                ):
                    for j in range(SUB_N):
                        time.sleep(0.001)
                        loading_bar.nested_advance()

                        if random() < 0.001:
                            loading_bar.inc_stat("errors")

                        if random() < 0.005:
                            loading_bar.inc_stat("warnings")

except KeyboardInterrupt:
    sys.exit(1)
