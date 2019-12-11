# =============================================================================
# Minet Facebook Post Stats CLI Action
# =============================================================================
#
# Logic of the `fb post-stats` action.
#
import sys
from tqdm import tqdm

from minet.cli.utils import DummyTqdmFile
from minet.cli.facebook.utils import grab_facebook_cookie


def facebook_post_stats_action(namespace):

    # Grabbing cookie
    cookie = grab_facebook_cookie(namespace)

    # Handling output
    if namespace.output is None:
        output_file = DummyTqdmFile(sys.stdout)
    else:
        output_file = open(namespace.output, 'w')

    print(cookie)
