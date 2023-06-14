from minet.cli.argparse import command

DUMP_QUEUE_COMMAND = command(
    "dump-queue",
    "minet.cli.dump.dump_queue",
    title="Minet Dump Queue Command",
    description="""
        Debug command that can be used to dump a crawler's queue
        and see what's inside.
    """,
    epilog="""
        Examples:

        . Dumping a queue:
            $ minet dump-queue ./path-to-queue-directory
    """,
    arguments=[
        {"name": "queue_dir", "help": "Path to the queue's directory."},
    ],
)

DUMP_URLS_COMMAND = command(
    "dump-urls",
    "minet.cli.dump.dump_urls",
    title="Minet Dump Urls Command",
    description="""
        Debug command that can be used to dump a crawler's url store
        and see what's inside.
    """,
    epilog="""
        Examples:

        . Dumping a url store:
            $ minet dump-urls ./path-to-urls-directory
    """,
    arguments=[
        {"name": "urls_dir", "help": "Path to the url store's directory."},
    ],
)
