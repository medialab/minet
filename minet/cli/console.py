# =============================================================================
# Minet Rich Console
# =============================================================================
#
# Rich console instance used by minet CLI.
#
from rich.console import Console
from rich.theme import Theme

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

console = Console(theme=MINET_THEME, stderr=True)

if __name__ == "__main__":
    for color in MINET_COLORS:
        console.print(color, style=color)
