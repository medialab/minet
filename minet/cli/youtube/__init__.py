# =============================================================================
# Minet Youtube CLI Action
# =============================================================================
#
# Logic of the `yt` action.
#
from minet.cli.utils import open_output_file, die


def check_key(namespace):

    # A key is required to used the API
    if not namespace.key:
        die([
            'A key is required to access YouTube API.',
            'You can provide it using the --key argument.'
        ])


def youtube_action(namespace):

    output_file = open_output_file(
        namespace.output,
        flag='w'
    )

    if namespace.yt_action == 'videos':
        check_key(namespace)

        from minet.cli.youtube.videos import videos_action
        videos_action(namespace, output_file)

    elif namespace.yt_action == 'comments':
        check_key(namespace)

        from minet.cli.youtube.comments import comments_action
        comments_action(namespace, output_file)

    elif namespace.yt_action == 'captions':
        from minet.cli.youtube.captions import captions_action
        captions_action(namespace, output_file)

    elif namespace.yt_action == 'search':
        check_key(namespace)

        from minet.cli.youtube.search import search_action
        search_action(namespace, output_file)

    if namespace.output is not None:
        output_file.close()
