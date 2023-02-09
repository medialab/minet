# =============================================================================
# Minet Youtube Comments CLI Action
# =============================================================================
#
# Action retrieving the comments of YouTube videos using the API.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.youtube import YouTubeAPIClient
from minet.youtube.constants import YOUTUBE_COMMENT_CSV_HEADERS
from minet.youtube.exceptions import (
    YouTubeDisabledCommentsError,
    YouTubeVideoNotFoundError,
    YouTubeExclusiveMemberError,
    YouTubeUnknown403Error,
)


@with_enricher_and_loading_bar(
    headers=YOUTUBE_COMMENT_CSV_HEADERS,
    desc="Retrieving comments",
    unit="comment",
    stats={"videos": 0},
)
def action(cli_args, enricher, loading_bar):
    client = YouTubeAPIClient(cli_args.key)

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
