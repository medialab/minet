import time

from minet.cli.loading_bar import LoadingBar

N = 1000

with LoadingBar(title="Processing range", total=N) as bar:
    for i in range(N):
        time.sleep(0.005)
        bar.update()
