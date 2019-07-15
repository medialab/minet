# =============================================================================
# Minet CrowdTangle CLI Action
# =============================================================================
#
# Logic of the `ct` action.
#
import sys

from minet.cli.crowdtangle.posts import crowdtangle_posts_action
from minet.cli.utils import DummyTqdmFile


def crowdtangle_action(namespace):

    # A token is needed to be able to access the API
    if not namespace.token:
        print('A token is needed to be able to access CrowdTangle\'s API.', file=sys.stderr)
        print('You can provide one using the `--token` argument.', file=sys.stderr)
        sys.exit(1)

    if namespace.output is None:
        output_file = DummyTqdmFile(sys.stdout)
    else:
        output_file = open(namespace.output, 'w')

    if namespace.ct_action == 'posts':
        crowdtangle_posts_action(namespace, output_file)

    # Cleanup
    if namespace.output is not None:
        output_file.close()
