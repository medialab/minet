from minet.cli.argparse import command, InputAction

PREVIEW_COMMAND = command(
    "preview",
    "minet.cli.preview.preview",
    title="Minet View Command",
    help="""
        A utility command one can use to preview the content
        of a CSV file directly from the comfort of a terminal.
    """,
    arguments=[{"name": "file", "action": InputAction, "help": "CSV file to preview."}],
)
