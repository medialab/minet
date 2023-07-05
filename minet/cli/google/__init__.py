# =============================================================================
# Minet Google CLI Action
# =============================================================================
#
# Logic of the `google` action.
#
from minet.cli.argparse import command

GOOGLE_SHEETS_SUBCOMMAND = command(
    "sheets",
    "minet.cli.google.sheets",
    title="Minet Google Sheets Command",
    description="""
        Grab the given google spreadsheet as a CSV file from
        its url, its sharing url or id.

        It can access public spreadsheets without issues, but to
        you will need to tell the command how to retrieve Google
        drive authentication cookies to also be able to access
        private ones.

        Also note that by default, the command will try to access
        your spreadsheet using your first 4 connected Google
        accounts.

        If you have more connected accounts or know beforehand
        to which account some spreadsheets are tied to, be sure
        to give --authuser.
    """,
    epilog="""
        Examples:

        . Exporting from the spreadsheet id:
            $ minet google sheets 1QXQ1yaNYrVUlMt6LQ4jrLGt_PvZI9goozYiBTgaC4RI > file.csv

        . Using your Firefox authentication cookies:
            $ minet google sheets --cookie firefox 1QXQ1yaNYrVUlMt6LQ4jrLGt_PvZI9goozYiBTgaC4RI > file.csv
    """,
    arguments=[
        {
            "name": "url",
            "help": "Url, sharing url or id of the spreadsheet to export.",
        },
        {
            "flags": ["-a", "--authuser"],
            "help": "Connected google account number to use.",
            "type": int,
        },
        {
            "flags": ["-c", "--cookie"],
            "help": 'Google Drive cookie or browser from which to extract it (supports "firefox", "chrome", "chromium", "opera" and "edge").',
        },
    ],
)

GOOGLE_COMMAND = command(
    "google",
    "minet.cli.google",
    "Minet Google Command",
    description="""
        Collect data from Google.
    """,
    subcommands=[GOOGLE_SHEETS_SUBCOMMAND],
)
