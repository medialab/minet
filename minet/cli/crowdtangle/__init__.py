# =============================================================================
# Minet CrowdTangle CLI Action
# =============================================================================
#
# Logic of the `ct` action.
#
import sys

from minet.cli.utils import open_output_file, die


def crowdtangle_action(cli_args):

    # A token is needed to be able to access the API
    if not cli_args.token:
        die([
            'A token is needed to be able to access CrowdTangle\'s API.',
            'You can provide one using the `--token` argument.'
        ])

    output_file = open_output_file(
        cli_args.output,
        flag='a+' if getattr(cli_args, 'resume', False) else 'w'
    )

    if cli_args.ct_action == 'posts':
        from minet.cli.crowdtangle.posts import crowdtangle_posts_action

        crowdtangle_posts_action(cli_args, output_file)

    elif cli_args.ct_action == 'posts-by-id':
        from minet.cli.crowdtangle.posts_by_id import crowdtangle_posts_by_id_action

        crowdtangle_posts_by_id_action(cli_args, output_file)

    elif cli_args.ct_action == 'lists':
        from minet.cli.crowdtangle.lists import crowdtangle_lists_action

        crowdtangle_lists_action(cli_args, output_file)

    elif cli_args.ct_action == 'leaderboard':
        from minet.cli.crowdtangle.leaderboard import crowdtangle_leaderboard_action

        crowdtangle_leaderboard_action(cli_args, output_file)

    elif cli_args.ct_action == 'search':
        from minet.cli.crowdtangle.search import crowdtangle_search_action

        crowdtangle_search_action(cli_args, output_file)

    elif cli_args.ct_action == 'summary':
        from minet.cli.crowdtangle.summary import crowdtangle_summary_action

        crowdtangle_summary_action(cli_args, output_file)

    # Cleanup
    if cli_args.output is not None:
        output_file.close()
