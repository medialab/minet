# =============================================================================
# Minet Youtube Comments CLI Action
# =============================================================================
#
# Action retrieving the comments of YouTube videos using the API.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.youtube import YouTubeAPIClient
from minet.youtube.types import YouTubeComment
from minet.youtube.exceptions import (
    YouTubeDisabledCommentsError,
    YouTubeNotFoundError,
    YouTubeExclusiveMemberError,
    YouTubeUnknown403Error,
)


@with_enricher_and_loading_bar(
    headers=YouTubeComment,
    title="Collecting video comments",
    unit="videos",
    sub_unit="comments",
    nested=True,
    stats=[
        {"name": "disabled", "style": "warning"},
        {"name": "not-found", "style": "error"},
        {"name": "exclusive-member", "style": "warning"},
        {"name": "403", "style": "error"},
    ],
)
def action(cli_args, enricher, loading_bar):
    client = YouTubeAPIClient(cli_args.key)

    for row, video in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(video):
            generator = client.comments(video)

            try:
                for comment in generator:
                    enricher.writerow(row, comment)
                    loading_bar.nested_advance()

            except YouTubeDisabledCommentsError:
                loading_bar.inc_stat("disabled")

            except YouTubeNotFoundError:
                loading_bar.inc_stat("not-found")

            except YouTubeExclusiveMemberError:
                loading_bar.inc_stat("exclusive-member")

            except YouTubeUnknown403Error:
                loading_bar.inc_stat("403")
