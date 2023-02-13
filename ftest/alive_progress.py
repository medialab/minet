import time

from minet.cli.loading_bar import LoadingBar

N = 1000

with LoadingBar(title="Processing range", total=N, dual_line=True) as bar:
    for i in range(N):
        time.sleep(0.005)
        bar.update(text="Counted up to: %i" % i)

        if i % 100 == 0:
            bar.inc_stat("errors")
