from typing import Dict

from ebbe import noop
from click.types import STRING, BOOL
from textual.app import App
from textual.screen import Screen
from rich.highlighter import ReprHighlighter
from trogon.trogon import Trogon, CommandBuilder
from trogon.introspect import (
    CommandName,
    CommandSchema,
    OptionSchema,
    MultiValueParamData,
)


def introspect_minet(commands) -> Dict[CommandName, CommandSchema]:
    data = {}

    # root_cmd_name = CommandName("root")
    # data[root_cmd_name] = CommandSchema('root', function=noop)
    # app = data[root_cmd_name]

    for command in commands:
        if "subparsers" in command:
            continue

        name = CommandName(command["name"])

        arguments = []
        options = []

        for arg in command.get("arguments", []):
            if "flag" in arg:
                options.append(
                    OptionSchema(
                        [arg["flag"]],
                        type=STRING if arg.get("action") != "store_true" else BOOL,
                        default=MultiValueParamData([]),
                        help=arg.get("help"),
                    )
                )

        command_schema = CommandSchema(
            name=name,
            function=noop,
            docstring=command.get("description", ""),
            options=options,
        )

        data[name] = command_schema

    return data


class MinetCommandBuilder(CommandBuilder):
    def __init__(
        self,
        commands,
        app_name: str,
        version: str,
        name=None,
        id=None,
        classes=None,
    ):
        Screen.__init__(self, name, id, classes)
        self.command_data = None
        self.is_grouped_cli = True
        self.command_schemas = introspect_minet(commands)
        self.click_app_name = app_name

        self.version = version

        self.highlighter = ReprHighlighter()


Trogon.on_mount = noop


class MinetTrogon(Trogon):
    def __init__(
        self,
        commands,
        app_name: str,
        version: str,
    ) -> None:
        App.__init__(self)
        self.post_run_command: list[str] = []
        self.is_grouped_cli = True
        self.execute_on_exit = False
        self.app_name = app_name
        self.version = version
        self.commands = commands

    def on_mount(self):
        self.push_screen(
            MinetCommandBuilder(self.commands, self.app_name, self.version)
        )


if __name__ == "__main__":
    from minet.__version__ import __version__
    from minet.cli.commands import MINET_COMMANDS

    MinetTrogon(MINET_COMMANDS, "minet", __version__).run()
