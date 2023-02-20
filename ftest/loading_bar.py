import time
import sys

from minet.cli.loading_bar import LoadingBar


N = 1_000
try:
    with LoadingBar(
        title="Processing",
        total=N,
        unit="apples",
        # show_label=True,
        stats=[
            {"name": "errors", "style": "error"},
            {"name": "warnings", "style": "warning"},
        ],
    ) as loading_bar:
        for i in range(N):
            time.sleep(0.005)

            # loading_bar.update(label="Currently processing %i" % i)

            if i % 100 == 0:
                print("Reached", i)

            if i % 156 == 0:
                loading_bar.update(errors=1)

            if i % 133 == 0:
                loading_bar.update(warnings=1)

            loading_bar.advance()
except KeyboardInterrupt:
    sys.exit(1)
