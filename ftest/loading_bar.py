import time
import sys

from minet.cli.loading_bar import LoadingBar


N = 10
SUB_N = 1_000
try:
    with LoadingBar(
        title="Processing",
        total=None,
        unit="apples",
        stats=[
            {"name": "errors", "style": "error"},
            {"name": "warnings", "style": "warning"},
        ],
        nested=True,
    ) as loading_bar:
        for i in range(N):
            for j in range(SUB_N):
                time.sleep(0.001)

            loading_bar.advance()

except KeyboardInterrupt:
    sys.exit(1)
