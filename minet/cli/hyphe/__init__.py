# =============================================================================
# Minet Hyphe CLI Action
# =============================================================================
#
# Logic of the `hyphe` action.
#
from argparse import FileType

from minet.cli.argparse import command, SplitterType, InputAction
from minet.cli.crawl import crawl_command

HYPHE_API_URL_ARGUMENT = {"name": "url", "help": "Url of the Hyphe API."}
HYPHE_CORPUS_ARGUMENT = {"name": "corpus", "help": "Id of the corpus."}
HYPHE_PASSWORD_ARGUMENT = {
    "flag": "--password",
    "help": "The corpus's password if required.",
}


def hyphe_corpus_subcommand(*args, arguments=[], **kwargs):
    return command(
        *args,
        arguments=[HYPHE_API_URL_ARGUMENT, HYPHE_CORPUS_ARGUMENT]
        + arguments
        + [HYPHE_PASSWORD_ARGUMENT],
        **kwargs
    )


HYPHE_CRAWL_SUBCOMMAND = crawl_command(
    "crawl",
    "minet.cli.hyphe.crawl",
    title="Minet Hyphe Crawl Command",
    description="""
        Specialized crawl command that can be used to reproduce
        a Hyphe crawl from a corpus exported in CSV.
    """,
    epilog="""
        Examples:

        . Reproducing a crawl:
            $ minet hyphe crawl corpus.csv
    """,
    unique=True,
    accept_input=False,
    default_folder_strategy="fullpath",
    default_throttle=0,
    default_connect_timeout=15,
    default_timeout=60,
    default_retries=3,
    force_spoof_user_agent=True,
    force_stateful_redirects=True,
    arguments=[
        {
            "name": "corpus",
            "action": InputAction,
            "help": "Path to the Hyphe corpus exported to CSV.",
        },
        {
            "flag": "--id-column",
            "default": "ID",
            "help": "Name of the CSV column containing the webentity ids.",
        },
        {
            "flag": "--status-column",
            "default": "STATUS",
            "help": "Name of the CSV column containing the webentity statuses.",
        },
        {
            "flag": "--prefixes-column",
            "default": "PREFIXES AS URL",
            "help": "Name of the CSV column containing the webentity prefixes, separated by --prefix-separator.",
        },
        {
            "flag": "--prefix-separator",
            "default": " ",
            "help": "Separator character for the webentity prefixes.",
        },
        {
            "flag": "--start-pages-column",
            "default": "START PAGES",
            "help": "Name of the CSV column containing the webentity start pages, separated by --start-page-separator.",
        },
        {
            "flag": "--start-page-separator",
            "default": " ",
            "help": "Separator character for the webentity start pages.",
        },
        {
            "flag": "--ignore-internal-links",
            "help": "Whether not to write links internal to a webentity on disk.",
            "action": "store_true",
        },
    ],
)


HYPHE_DECLARE_SUBCOMMAND = hyphe_corpus_subcommand(
    "declare",
    "minet.cli.hyphe.declare",
    title="Minet Hyphe Declare Command",
    description="""
        Command that can be used to declare series of webentities
        in a corpus.

        It is ideal to start or restart a corpus using the same exact
        webentity declarations as another one.
    """,
    epilog="""
        Examples:

        . Declaring webentities from a Hyphe export:
            $ minet hyphe declare http://myhyphe.com/api/ target-corpus export.csv
    """,
    total=True,
    arguments=[
        {
            "name": "webentities",
            "help": "CSV file of webentities (exported from Hyphe).",
            "type": FileType("r", encoding="utf-8"),
        }
    ],
)

HYPHE_DESTROY_SUBCOMMAND = hyphe_corpus_subcommand(
    "destroy",
    "minet.cli.hyphe.destroy",
    title="Minet Hyphe Destroy Command",
    description="""
        Command that can be used to destroy a corpus entirely.
    """,
    epilog="""
        Examples:

        . Destroying a corpus:
            $ minet hyphe destroy http://myhyphe.com/api/ my-corpus
    """,
)

HYPHE_DUMP_SUBCOMMAND = hyphe_corpus_subcommand(
    "dump",
    "minet.cli.hyphe.dump",
    title="Minet Hyphe Dump Command",
    description="""
        Command dumping page-level information from a given
        Hyphe corpus.
    """,
    epilog="""
        Examples:

        . Dumping a corpus into the ./corpus directory:
            $ minet hyphe dump http://myhyphe.com/api/ corpus-name -O corpus
    """,
    arguments=[
        {
            "flags": ["-O", "--output-dir"],
            "help": "Output directory for dumped files. Will default to some name based on corpus name.",
        },
        {
            "flag": "--body",
            "help": "Whether to download pages body.",
            "action": "store_true",
        },
        {
            "flag": "--statuses",
            "help": 'Webentity statuses to dump, separated by comma. Possible statuses being "IN", "OUT", "UNDECIDED" and "DISCOVERED".',
            "type": SplitterType(),
        },
        {
            "flag": "--page-count",
            "help": "Number of pages to download per pagination call. Tweak if corpus has large pages or if the network is unreliable.",
            "type": int,
            "default": 500,
        },
    ],
)

HYPHE_RESET_SUBCOMMAND = hyphe_corpus_subcommand(
    "reset",
    "minet.cli.hyphe.reset",
    title="Minet Hyphe Reset Command",
    description="""
        Command that can be used to reset a corpus entirely.
    """,
    epilog="""
        Examples:

        . Resetting a corpus:
            $ minet hyphe reset http://myhyphe.com/api/ my-corpus
    """,
)

HYPHE_TAG_SUBCOMMAND = hyphe_corpus_subcommand(
    "tag",
    "minet.cli.hyphe.tag",
    title="Minet Hyphe Tag Command",
    description="""
        Command that can be used to tag webentities in batch using
        metadata recorded in a CSV file.
    """,
    epilog="""
        Examples:

        . Tag webentities from two columns of CSV file:
            $ minet hyphe tag http://myhyphe.com/api/ my-corpus webentity_id type,creator metadata.csv
    """,
    total=True,
    arguments=[
        {
            "name": "webentity_id_column",
            "help": "Column of the CSV file containing the webentity ids.",
        },
        {
            "name": "tag_columns",
            "help": "Columns, separated by comma, to use as tags.",
            "type": SplitterType(),
        },
        {
            "name": "data",
            "help": "CSV file of webentities (exported from Hyphe).",
            "type": FileType("r", encoding="utf-8"),
        },
        {
            "flag": "--separator",
            "help": "Separator use to split multiple tag values in the same column.",
            "default": "|",
        },
    ],
)

HYPHE_COMMAND = command(
    "hyphe",
    "minet.cli.hyphe",
    "Minet Hyphe Command",
    description="""
        Commands related to the Hyphe web crawler.
    """,
    subcommands=[
        HYPHE_CRAWL_SUBCOMMAND,
        HYPHE_DECLARE_SUBCOMMAND,
        HYPHE_DESTROY_SUBCOMMAND,
        HYPHE_DUMP_SUBCOMMAND,
        HYPHE_RESET_SUBCOMMAND,
        HYPHE_TAG_SUBCOMMAND,
    ],
)
