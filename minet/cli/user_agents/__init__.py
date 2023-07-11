from minet.cli.argparse import command

USER_AGENTS_UPDATE_SUBCOMMAND = command(
    "update",
    "minet.cli.user_agents.update",
    title="Minet User Agents Update Command",
    description="""
        Command used to update the internal list of
        plausible User Agent strings used by minet
        to spoof some requests.

        The list of user agents come from the website:
        www.useragents.me
    """,
    no_output=True,
)

USER_AGENTS_EXPORT_SUBCOMMAND = command(
    "export",
    "minet.cli.user_agents.export",
    title="Minet User Agents Export Command",
    description="""
        Command used to export the internal list of
        plausible User Agent strings used by minet
        to spoof some requests.

        The list of user agents come from the website:
        www.useragents.me
    """,
)

USER_AGENTS_RANDOM_SUBCOMMAND = command(
    "random",
    "minet.cli.user_agents.random",
    title="Minet User Agents Random Command",
    description="""
        Command used to return a random plausible
        User Agent.

        The list of user agents come from the website:
        www.useragents.me
    """,
)

USER_AGENTS_COMMAND = command(
    "user-agents",
    "minet.cli.user_agents",
    title="Minet User Agents Command",
    aliases=["ua"],
    subcommands=[
        USER_AGENTS_UPDATE_SUBCOMMAND,
        USER_AGENTS_EXPORT_SUBCOMMAND,
        USER_AGENTS_RANDOM_SUBCOMMAND,
    ],
)
