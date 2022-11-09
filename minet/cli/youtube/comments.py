# =============================================================================
# Minet Youtube Comments CLI Action
# =============================================================================
#
# Action retrieving the comments of YouTube videos using the API.
#
import casanova

from minet.cli.utils import LoadingBar
from minet.youtube import YouTubeAPIClient
from minet.youtube.constants import YOUTUBE_COMMENT_CSV_HEADERS
from minet.youtube.exceptions import (
    YouTubeDisabledCommentsError,
    YouTubeVideoNotFoundError,
    YouTubeExclusiveMemberError,
    YouTubeUnknown403Error,
)


def comments_action(cli_args):
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=YOUTUBE_COMMENT_CSV_HEADERS,
        keep=cli_args.select,
    )

    loading_bar = LoadingBar("Retrieving comments", unit="comment", stats={"videos": 0})

    def before_sleep_until_midnight(seconds):
        loading_bar.print(
            "API limits reached. Will now wait until midnight Pacific time!"
        )

    client = YouTubeAPIClient(
        cli_args.key, before_sleep_until_midnight=before_sleep_until_midnight
    )

    for row, video in enricher.cells(cli_args.column, with_rows=True):
        generator = client.comments(video)

        try:
            for comment in generator:
                loading_bar.update()
                enricher.writerow(row, comment.as_csv_row())

            loading_bar.inc("videos")
        except YouTubeDisabledCommentsError:
            loading_bar.print(
                "\nYouTube disabled the comments for this video: %s" % video
            )
        except YouTubeVideoNotFoundError:
            loading_bar.print("\nThis YouTube video can't be found: %s" % video)
        except YouTubeExclusiveMemberError:
            loading_bar.print(
                "\nThis video is reserved for exclusive members: %s" % video
            )
        except YouTubeUnknown403Error:
            loading_bar.print("\nAn unknown 403 error has occured: %s" % video)
