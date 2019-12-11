# =============================================================================
# Minet Facebook Post Stats CLI Action
# =============================================================================
#
# Logic of the `fb post-stats` action.
#
from tqdm import tqdm

from minet.cli.utils import open_output_file
from minet.cli.facebook.utils import grab_facebook_cookie


def facebook_post_stats_action(namespace):

    # Grabbing cookie
    cookie = grab_facebook_cookie(namespace)

    # Handling output
    output_file = open_output_file(namespace.output)

    print(cookie)
