# =============================================================================
# Minet Mediacloud CLI Action
# =============================================================================
#
# Logic of the `mc` action.
#
from minet.cli.utils import die, open_output_file


def mediacloud_action(namespace):

    # A token is needed to be able to access the API
    if not namespace.token:
        die([
            'A token is needed to be able to access Mediacloud\'s API.',
            'You can provide one using the `--token` argument.'
        ])

    output_file = open_output_file(namespace.output)

    from minet.cli.mediacloud.topic import mediacloud_topic_action
    mediacloud_topic_action(namespace, output_file)

    output_file.close()
