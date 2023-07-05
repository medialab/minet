#!/usr/bin/env python
# =============================================================================
# Minet CLI Endpoint
# =============================================================================
#
# CLI endpoint of the Minet library.
#
from minet.__version__ import __identifier__
from minet.cli.run import run
from minet.cli.commands import MINET_COMMANDS


def main():
    run("minet", __identifier__, MINET_COMMANDS)


if __name__ == "__main__":
    main()
