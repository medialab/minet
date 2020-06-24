# =============================================================================
# Minet Youtube CLI Action
# =============================================================================
#
# Logic of the `yt` action.
#
from minet.cli.utils import open_output_file


def youtube_action(namespace):

    output_file = open_output_file(
        namespace.output,
        flag='w'
    )

    if namespace.yt_action == 'url-parse':
        from minet.cli.youtube.url_parse import url_parse_action
        url_parse_action(namespace, output_file)

    elif namespace.yt_action == 'videos':
        from minet.cli.youtube.videos import videos_action
        videos_action(namespace, output_file)

    elif namespace.yt_action == 'comments':
        from minet.cli.youtube.comments import comments_action
        comments_action(namespace, output_file)

    elif namespace.yt_action == 'captions':
        from minet.cli.youtube.captions import captions_action
        captions_action(namespace, output_file)

    if namespace.output is not None:
        output_file.close()
