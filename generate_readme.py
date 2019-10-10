import re
from textwrap import dedent

from minet.cli.__main__ import build_parser, get_subparser
from minet.cli.commands import MINET_COMMANDS

TEMPLATE_RE = re.compile(r'<%\s+([A-Za-z/\-]+)\s+%>')


def replacer(match):
    keys = match.group(1).split('/')

    target = get_subparser(subparser_index, keys)

    return dedent('''
        ```
        %s
        ```
    ''') % target.format_help()

parser, subparser_index = build_parser(MINET_COMMANDS)

with open('./README.template.md') as f:
    template_string = f.read()

template_string = re.sub(TEMPLATE_RE, replacer, template_string)

print(template_string)
