import time
import sys

from minet.cli.loading_bar import LoadingBar


N = 1_000
try:
    with LoadingBar(title="Processing", total=N, unit="apples") as loading_bar:
        for i in range(N):
            time.sleep(0.005)
            loading_bar.advance()
except KeyboardInterrupt:
    sys.exit(1)
