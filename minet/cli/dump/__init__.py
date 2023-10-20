from minet.cli.argparse import command, InputAction

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

DUMP_GRAPH_COMMAND = command(
    "dump-graph",
    "minet.cli.dump.dump_graph",
    title="Minet Dump Graph Command",
    description="""
        Debug command that can be used to dump a crawler's graph from
        a jobs csv and manipulate it as a network.

        The export file is in json with a Graphology format.
    """,
    epilog="""
        Examples:

        . Dumping a graph file from crawler jobs:
            $ minet dump-graph -i ./jobs.csv > graph.json
    """,
    select=True,
    arguments=[
        {
            "flags": ["-i", "--input"],
            "help": "Path to crawler's jobs csv file.",
            "action": InputAction,
        },
        {
            "flags": ["-l", "--label"],
            "help": "Specify the CSV column to use for graph's nodes label",
            "default": "url",
        },
    ],
)
