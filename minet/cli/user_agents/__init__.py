from minet.cli.argparse import command, subcommand
from minet.cli.exceptions import InvalidArgumentsError

USER_AGENTS_UPDATE_SUBCOMMAND = subcommand(
    "update",
    "minet.cli.user_agents.update",
    title="Minet User Agents Update Command",
    description="""
        Command tu update the list of user agents
        used by minet http requests.

        The list of user agents come from the website
        www.useragents.me
    """,
)

USER_AGENTS_EXPORT_SUBCOMMAND = subcommand(
    "export",
    "minet.cli.user_agents.export",
    title="Minet User Agents Export Command",
    description="""
        Command to export the user agents stored
        in the minet's module. The export format
        is CSV.
    """,
)

USER_AGENTS_RANDOM_SUBCOMMAND = subcommand(
    "random",
    "minet.cli.user_agents.random",
    title="Minet User Agents Random Command",
    description="""
        Command to export a random user agent stored
        in the minet's module.

        The percent provided is « the relative share
        of each useragent » detected by useragents.me
    """,
)

USER_AGENTS_COMMAND = command(
    "useragents",
    "minet.cli.user_agents",
    title="Minet User Agents Command",
    aliases=["ua"],
    subcommands=[
        USER_AGENTS_UPDATE_SUBCOMMAND,
        USER_AGENTS_EXPORT_SUBCOMMAND,
        USER_AGENTS_RANDOM_SUBCOMMAND
    ],
)
