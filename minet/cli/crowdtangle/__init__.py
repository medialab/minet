# =============================================================================
# Minet CrowdTangle CLI Action
# =============================================================================
#
# Logic of the `ct` action.
#
import sys

from minet.cli.utils import open_output_file, die


def crowdtangle_action(namespace):

    # A token is needed to be able to access the API
    if not namespace.token:
        die([
            'A token is needed to be able to access CrowdTangle\'s API.',
            'You can provide one using the `--token` argument.'
        ])

    output_file = open_output_file(
        namespace.output,
        flag='a+' if getattr(namespace, 'resume', False) else 'w'
    )

    if namespace.ct_action == 'posts':
        from minet.cli.crowdtangle.posts import crowdtangle_posts_action

        crowdtangle_posts_action(namespace, output_file)

    elif namespace.ct_action == 'posts-by-id':
        from minet.cli.crowdtangle.posts_by_id import crowdtangle_posts_by_id_action

        crowdtangle_posts_by_id_action(namespace, output_file)

    elif namespace.ct_action == 'lists':
        from minet.cli.crowdtangle.lists import crowdtangle_lists_action

        crowdtangle_lists_action(namespace, output_file)

    elif namespace.ct_action == 'leaderboard':
        from minet.cli.crowdtangle.leaderboard import crowdtangle_leaderboard_action

        crowdtangle_leaderboard_action(namespace, output_file)

    elif namespace.ct_action == 'search':
        from minet.cli.crowdtangle.search import crowdtangle_search_action

        crowdtangle_search_action(namespace, output_file)

    elif namespace.ct_action == 'summary':
        from minet.cli.crowdtangle.summary import crowdtangle_summary_action

        crowdtangle_summary_action(namespace, output_file)

    # Cleanup
    if namespace.output is not None:
        output_file.close()
