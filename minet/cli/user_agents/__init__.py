from minet.cli.argparse import command, subcommand
from minet.cli.exceptions import InvalidArgumentsError
from minet.cli.argparse import InputAction

def check_arguments(cli_args):
    if not cli_args.input and not cli_args.user_agent_column:
        raise InvalidArgumentsError("You need to mention the CSV file path and user agents' column name to use your own list of user agents.")

USER_AGENTS_UPDATE_SUBCOMMAND = subcommand(
    "update",
    "minet.cli.user_agents.update",
    title="Minet User Agents Update Command",
    description="""
        Command tu update the list of user agents
        used by minet http requests.

        By default, it fetches a list from the
        internet (from www.useragentsme.com) but you
        can use your own list of user agents from
        a csv file (using -i, --input flag).
    """
)

USER_AGENTS_COMMAND = command(
    "useragents",
    "minet.cli.user_agents",
    title="Minet User Agents Command",
    aliases=["ua"],
    subcommands=[
        USER_AGENTS_UPDATE_SUBCOMMAND
    ]
)
