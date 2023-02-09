from minet.cli.commands import MINET_COMMANDS
from minet.cli.argparse import template_readme

with open("./docs/cli.template.md") as f:
    template_string = f.read()

print(template_readme(template_string, MINET_COMMANDS))
