# =============================================================================
# Minet Twitter CLI Action
# =============================================================================
#
# Logic of the `tw` action.
#
from minet.cli.commands import command

from minet.cli.twitter.users import TWITTER_USERS_SUBCOMMAND

TWITTER_COMMAND = command(
    "twitter",
    "minet.cli.twitter",
    "Minet Twitter Command",
    aliases=["tw"],
    description="""
        Gather data from Twitter.
    """,
    subcommands=[TWITTER_USERS_SUBCOMMAND],
)
