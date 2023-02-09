from minet.cli.argparse import command
from minet.cli.run import run


def action(cli_args):
    print(cli_args)


EXTRA_COMMAND = command("extra", action, title="Extra Command")


if __name__ == "__main__":
    run("minet-extra", "1.0", [EXTRA_COMMAND])
