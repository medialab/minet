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

    if namespace.mc_action == 'medias':
        from minet.cli.mediacloud.medias import mediacloud_medias_action
        mediacloud_medias_action(namespace, output_file)

    if namespace.mc_action == 'topic':
        from minet.cli.mediacloud.topic import mediacloud_topic_action
        mediacloud_topic_action(namespace, output_file)

    elif namespace.mc_action == 'search':
        from minet.cli.mediacloud.search import mediacloud_search_action
        mediacloud_search_action(namespace, output_file)

    output_file.close()
