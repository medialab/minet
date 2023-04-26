from minet.__version__ import __identifier__
from minet.cli.run import run
from minet.cli.commands import MINET_COMMANDS


def run_command(args: str) -> None:
    run("minet", __identifier__, MINET_COMMANDS, args)
