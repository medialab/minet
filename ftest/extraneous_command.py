from minet.cli.argparse import command
from minet.cli.run import run

EXTRA_COMMAND = command("extra", "ftest.extraneous_command", title="Extra Command")


def action(cli_args):
    print(cli_args)


if __name__ == "__main__":
    run("minet-extra", "1.0", [EXTRA_COMMAND])
