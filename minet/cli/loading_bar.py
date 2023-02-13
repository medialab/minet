import os
import sys
import shutil
from typing import Optional
from types import SimpleNamespace
from alive_progress import alive_bar
from alive_progress.animations import frame_spinner_factory

DEFAULT_SPINNER = frame_spinner_factory("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏")

# NOTE: until the library is patched, we need to take into account
# the fact that the stderr cols are not computed correctly
def apply_alive_progress_patch():
    def patched_new(original):
        write = original.write
        flush = original.flush

        def cols():
            if hasattr(original, "fileno") and callable(original.fileno):
                fileno = original.fileno()
                if fileno in (sys.__stdout__.fileno(), sys.__stderr__.fileno()):
                    return os.get_terminal_size(fileno)[0]

            # more resilient one, although 7x slower than os' one.
            return shutil.get_terminal_size()[0]

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
        clear_end_screen = _ansi_escape_sequence(
            "J"
        )  # clears screen from cursor: CSI J.
        hide_cursor = _ansi_escape_sequence("?25l")  # hides the cursor: CSI ? 25 l.
        show_cursor = _ansi_escape_sequence("?25h")  # shows the cursor: CSI ? 25 h.
        carriage_return = "\r"

        return SimpleNamespace(**locals())

    import alive_progress.utils.terminal.tty as module_to_patch

    module_to_patch.new = patched_new


apply_alive_progress_patch()


class LoadingBar(object):
    def __init__(
        self,
        total: int = None,
        unit: str = "items",
        title: Optional[str] = None,
        dual_line: bool = False,
    ) -> None:
        self.title = title
        self.total = total
        self.dual_line = dual_line
        self.monitor = "{count}/{total} " + unit + " ({percent:.0%})"

        if total is None:
            self.monitor = "{count} " + unit

        self.bar_context = None
        self.bar = None

    def __enter__(self):
        self.bar_context = alive_bar(
            total=self.total,
            title=self.title,
            dual_line=self.dual_line,
            spinner=DEFAULT_SPINNER,
            enrich_print=False,
            monitor=self.monitor,
            file=sys.stderr,
            ctrl_c=False,
        )
        self.bar = self.bar_context.__enter__()

        return self

    def __exit__(self, *exc):
        return self.bar_context.__exit__(*exc)

    def update(self, count: int = 1, text: Optional[str] = None):
        self.bar(count)

        if text is not None:
            self.set_text(text)

    def set_title(self, title):
        self.bar.title = title

    def set_text(self, text):
        self.bar.text = text
