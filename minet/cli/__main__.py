#!/usr/bin/env python
# =============================================================================
# Minet CLI Endpoint
# =============================================================================
#
# CLI enpoint of the Minet library.
#
from minet.__version__ import __version__
from minet.cli.run import run
from minet.cli.commands import MINET_COMMANDS


def main():
    run("minet", __version__, MINET_COMMANDS)


if __name__ == "__main__":
    main()
