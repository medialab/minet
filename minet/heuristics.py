# =============================================================================
# Minet Heuristics
# =============================================================================
#
# Miscellaneous heuristics used by minet.
#
from typing import Optional


def should_spoof_ua_when_resolving(domain: Optional[str]) -> bool:
    if not domain:
        return False

    if domain == "t.co":
        return False

    return True
