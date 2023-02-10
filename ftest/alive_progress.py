import time
import sys
import csv
import os
import alive_progress.utils.terminal.tty
from alive_progress.styles import showtime, show_spinners
from alive_progress import alive_bar

import shutil
from types import SimpleNamespace


def my_new(original):
    write = original.write
    flush = original.flush

    def cols():
        # more resilient one, although 7x slower than os' one.
        return os.get_terminal_size(original.fileno())[0]

    def _ansi_escape_sequence(code, param=""):
        def inner(_available=None):  # because of jupyter.
            write(inner.sequence)

        inner.sequence = f"\x1b[{param}{code}"
        return inner

    def factory_cursor_up(num):
        return _ansi_escape_sequence("A", num)  # sends cursor up: CSI {x}A.

    clear_line = _ansi_escape_sequence(
        "2K\r"
    )  # clears the entire line: CSI n K -> with n=2.
    clear_end_line = _ansi_escape_sequence("K")  # clears line from cursor: CSI K.
    clear_end_screen = _ansi_escape_sequence("J")  # clears screen from cursor: CSI J.
    hide_cursor = _ansi_escape_sequence("?25l")  # hides the cursor: CSI ? 25 l.
    show_cursor = _ansi_escape_sequence("?25h")  # shows the cursor: CSI ? 25 h.
    carriage_return = "\r"

    return SimpleNamespace(**locals())


alive_progress.utils.terminal.tty.new = my_new

# show_spinners()

N = 1000

writer = csv.writer(sys.stdout)

with alive_bar(
    N,
    title="Processing range",
    unit="apple",
    dual_line=True,
    ctrl_c=False,
    file=sys.stderr,
) as bar:
    for i in range(N):
        time.sleep(0.005)
        bar.text(("Currently processing %i" % i) + "-" * 2000)

        if i % 100 == 0:
            print("test", i, file=sys.stderr)
            writer.writerow(["hello", "world", "are", "you", "there?"])

        bar()
