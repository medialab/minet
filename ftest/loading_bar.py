import time
import sys

from minet.cli.loading_bar import LoadingBar


N = 10
SUB_N = 1_000
try:
    with LoadingBar(
        title="Processing",
        total=2,
        unit="apples",
        sub_unit="videos",
        stats=[
            {"name": "errors", "style": "error"},
            {"name": "warnings", "style": "warning"},
        ],
        nested=True,
    ) as loading_bar:
        for i in range(N):
            with loading_bar.nested_task("Working on [info]%i[/info]" % i):
                for j in range(SUB_N):
                    time.sleep(0.001)
                    loading_bar.nested_advance()

except KeyboardInterrupt:
    sys.exit(1)
