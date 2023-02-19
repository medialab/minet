# =============================================================================
# Minet Rich Console
# =============================================================================
#
# Rich console instance used by minet CLI.
#
from rich.console import Console
from rich.theme import Theme

MINET_THEME = Theme()

console = Console(theme=MINET_THEME)
