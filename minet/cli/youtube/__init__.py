# =============================================================================
# Minet Youtube-parser CLI Action
# =============================================================================
#
# Logic of the `ct` action.
#
from minet.cli.utils import open_output_file

def youtube_action (namespace):

    output_file = open_output_file(
        namespace.output,
        flag='w'
    )

    if namespace.yt_action == 'parse-url':
        from minet.cli.youtube.parse_url import parse_url
        parse_url(namespace, output_file)

    if namespace.output is not None:
        output_file.close()
