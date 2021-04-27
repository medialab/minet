# =============================================================================
# Minet Heuristics
# =============================================================================
#
# Miscellaneous heuristics used by minet.
#


def should_spoof_ua_when_resolving(domain):
    if domain == 't.co':
        return False

    return True
