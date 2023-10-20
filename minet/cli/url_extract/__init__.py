from minet.cli.argparse import command, InputAction

URL_EXTRACT_COMMAND = command(
    "url-extract",
    "minet.cli.url_extract.url_extract",
    title="Minet Url Extract Command",
    description="""
        Extract urls from a CSV column containing either raw text or raw
        HTML.
    """,
    epilog="""
        Examples:

        . Extracting urls from a text column:
            $ minet url-extract text -i posts.csv > urls.csv

        . Extracting urls from a html column:
            $ minet url-extract html --from html -i posts.csv > urls.csv
    """,
    select=True,
    total=True,
    arguments=[
        {"name": "column", "help": "Name of the column containing text or html."},
        {"name": "input", "help": "Target CSV file.", "action": InputAction},
        {"flag": "--base-url", "help": "Base url used to resolve relative urls."},
        {
            "flag": "--from",
            "help": "Extract urls from which kind of source?",
            "choices": ["text", "html"],
            "default": "text",
        },
    ],
)
