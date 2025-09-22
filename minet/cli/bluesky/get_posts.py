from casanova import Enricher

from twitwi.bluesky.constants import POST_FIELDS
from twitwi.bluesky import format_post_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar

from minet.cli.bluesky.utils import with_bluesky_fatal_errors

from minet.bluesky import BlueskyHTTPClient


@with_bluesky_fatal_errors
@with_enricher_and_loading_bar(
    headers=POST_FIELDS,
    title="Getting Bluesky posts from URIs or URLs",
    unit="posts",
    nested=True,
)
def action(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    client = BlueskyHTTPClient(cli_args.identifier, cli_args.password)

    rows, param = zip(*enricher.cells(cli_args.column, with_rows=True))

    # In case the user passed full URLs instead of at:// URIs
    if param[0].startswith("at://did:"):
        uris = list(param)
    else:
        uris = [client.post_url_to_did_at_uri(url) for url in param]

    posts = [post for post in client.get_posts(uris)]

    for row, uri, post in zip(rows, uris, posts):
        with loading_bar.step(f"{uri}", sub_total=1):
            post_row = format_post_as_csv_row(post)
            enricher.writerow(row, post_row)
            loading_bar.nested_advance()
