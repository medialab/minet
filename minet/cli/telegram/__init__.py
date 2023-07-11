# =============================================================================
# Minet Telegram CLI Action
# =============================================================================
#
# Logic of the `tl` action.
#
from minet.cli.argparse import command

# TODO: this is a lazyloading problem
from minet.telegram.constants import TELEGRAM_DEFAULT_THROTTLE

THROTTLE_ARGUMENT = {
    "flag": "--throttle",
    "help": "Throttling time, in seconds, to wait between each request.",
    "type": float,
    "default": TELEGRAM_DEFAULT_THROTTLE,
}

TELEGRAM_CHANNEL_INFOS_SUBCOMMAND = command(
    "channel-infos",
    "minet.cli.telegram.channel_infos",
    title="Minet Telegram Channel-Infos Command",
    description="""
        Scrape a Telegram channel's infos.
    """,
    epilog="""
        Examples:
        . Scraping a channel's infos:
            $ minet telegram channel-infos nytimes > infos.csv
    """,
    variadic_input={
        "dummy_column": "channel_name",
        "item_label": "channel name / url",
        "item_label_plural": "channel names / urls",
    },
    arguments=[THROTTLE_ARGUMENT],
)

TELEGRAM_CHANNEL_MESSAGES_SUBCOMMAND = command(
    "channel-messages",
    "minet.cli.telegram.channel_messages",
    title="Minet Telegram Channel-Messages Command",
    description="""
        Scrape Telegram channel messages.
    """,
    epilog="""
        Examples:
        . Scraping a group's posts:
            $ minet telegram channel-messages nytimes > messages.csv
    """,
    variadic_input={
        "dummy_column": "channel_name",
        "item_label": "channel name / url",
        "item_label_plural": "channel names / urls",
    },
    arguments=[THROTTLE_ARGUMENT],
)

TELEGRAM_COMMAND = command(
    "telegram",
    "minet.cli.mediacloud",
    aliases=["tl"],
    title="Minet Telegram Command",
    description="""
        Collects data from Telegram.
    """,
    subcommands=[
        TELEGRAM_CHANNEL_INFOS_SUBCOMMAND,
        TELEGRAM_CHANNEL_MESSAGES_SUBCOMMAND,
    ],
)
