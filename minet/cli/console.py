# =============================================================================
# Minet Rich Console
# =============================================================================
#
# Rich console instance used by minet CLI.
#
from datetime import datetime
from rich.console import Console
from rich.theme import Theme
from rich.table import Table

NOW_TIME_FORMAT = r"%H:%M:%S"
NOW_DATETIME_FORMAT = r"%Y-%m-%d %H:%M:%S"

from minet.utils import message_flatmap

MINET_COLORS = {
    "info": "blue",
    "error": "#d42a20",
    "warning": "#fac22b",
    "cream": "#fcf3d9",
    "dark": "#02080b",
    "success": "green",
}

MINET_STYLES = {
    **MINET_COLORS,
    # Progress bar
    "bar.complete": MINET_COLORS["info"],
    "bar.finished": MINET_COLORS["success"],
    "progress.percentage": "",
    "progress.elapsed": "",
}
MINET_THEME = Theme(MINET_STYLES)


class MinetConsole(Console):
    def vprint(self, *messages):
        txt = message_flatmap(*messages)
        self.print(txt)

    def logh(self, header: str, *messages, style=None) -> None:
        txt = message_flatmap(*messages)

        table = Table.grid(padding=(0, 1), expand=True)

        table.add_column(style="log.time")
        table.add_column(ratio=1, overflow="fold", style=style)

        table.add_row(header, txt)

        self.print(table)

    def log_with_time(self, *messages, full=False, style=None):
        now = datetime.now().strftime(NOW_DATETIME_FORMAT if full else NOW_TIME_FORMAT)
        now = "[%s]" % now

        self.logh(now, *messages, style=style)


console = MinetConsole(theme=MINET_THEME, stderr=True, highlight=False)

__all__ = ["console"]

if __name__ == "__main__":
    for color in MINET_COLORS:
        console.print(color, style=color, end=" ")
    console.print("\n")

    console.log_with_time("hello")
