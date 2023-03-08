from minet.cli.argparse import command, InputAction

URL_JOIN_COMMAND = command(
    "url-join",
    "minet.cli.url_join.url_join",
    title="Minet Url Join Command",
    description="""
        Join two CSV files by matching them on columns containing urls. It
        works by indexing the first file's urls in a specialized
        URL trie to match them with the second file's urls.
    """,
    epilog="""
        Examples:

        . Joining two files:
            $ minet url-join url webentities.csv post_url posts.csv > joined.csv

        . Adding a prefix to first file's column names:
            $ minet url-join -p w_ url webentities.csv post_url posts.csv > joined.csv

        . Keeping only some columns from first file:
            $ minet url-join url webentities.csv post_url posts.csv -s url,id > joined.csv

        . Reading one of the files from stdin:
            $ xsv select url webentities.csv | minet url-join url - post_url posts.csv > joined.csv
    """,
    select=True,
    arguments=[
        {
            "name": "column1",
            "help": "Name of the column containing urls in the indexed file.",
        },
        {
            "name": "input1",
            "help": "Path to the file to index. Will understand `-` as stdin.",
            "action": InputAction,
            "nargs": None,
        },
        {
            "name": "column2",
            "help": "Name of the column containing urls in the second file.",
        },
        {
            "name": "input2",
            "help": "Path to the second file. Will understand `-` as stdin.",
            "action": InputAction,
            "nargs": None,
        },
        {
            "flags": ["-p", "--match-column-prefix"],
            "help": "Optional prefix to add to the first file's column names to avoid conflicts.",
            "default": "",
        },
        {"flag": "--separator", "help": "Split indexed url column by a separator?"},
    ],
)
