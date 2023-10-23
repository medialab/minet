# =============================================================================
# Minet Rich Console
# =============================================================================
#
# Rich console instance used by minet CLI.
#
from typing import Optional

from datetime import datetime
from rich.console import Console
from rich.theme import Theme
from rich.table import Table

from minet.utils import message_flatmap

NOW_TIME_FORMAT = r"%H:%M:%S"
NOW_DATETIME_FORMAT = r"%Y-%m-%d %H:%M:%S"

MINET_COLORS = {
    "info": "blue",
    "error": "#d42a20",
    "warning": "#fac22b",
    "cream": "#fcf3d9",
    "dark": "#02080b",
    "success": "green",
}

MINET_COLOR_BACKGROUNDS = {}

for name, style in MINET_COLORS.items():
    MINET_COLOR_BACKGROUNDS[name + "_background"] = "on " + style

MINET_STYLES = {
    **MINET_COLORS,
    **MINET_COLOR_BACKGROUNDS,
    # Progress bar
    "bar.complete": MINET_COLORS["info"],
    "bar.finished": MINET_COLORS["success"],
    "progress.percentage": "",
    "progress.elapsed": "",
}
MINET_THEME = Theme(MINET_STYLES)


class MinetConsole(Console):
    def vprint(self, *messages, style: Optional[str] = None):
        txt = message_flatmap(*messages)
        self.print(txt, style=style)

    def logh(self, header: str, *messages, style=None, header_style="log.time") -> None:
        txt = message_flatmap(*messages)

        table = Table.grid(padding=(0, 1), expand=True)

        table.add_column(style=header_style)
        table.add_column(ratio=1, overflow="fold", style=style)

        table.add_row(header, txt)

        self.print(table)

    def info(self, *messages):
        self.logh("info", *messages, header_style="info")

    def error(self, *messages):
        self.logh("error", *messages, header_style="error")

    def warning(self, *messages):
        self.logh("warning", *messages, header_style="warning")

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
