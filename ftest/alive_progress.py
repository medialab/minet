import time
import sys
import csv
from alive_progress.styles import showtime, show_spinners
from alive_progress import alive_bar

# show_spinners()

N = 1000

writer = csv.writer(sys.stdout)

with alive_bar(
    N,
    title="Processing range",
    unit="apple",
    dual_line=True,
    ctrl_c=False,
    file=sys.stdout,
) as bar:
    for i in range(N):
        time.sleep(0.005)
        bar.text(("Currently processing %i" % i) + "-" * 2000)

        if i % 100 == 0:
            print("test", i, file=sys.stderr)
            writer.writerow(["hello", "world", "are", "you", "there?"])

        bar()
