# =============================================================================
# Minet Hyphe Destroy CLI Action
# =============================================================================
#
# Logic of the `hyphe destroy` action.
#
from minet.hyphe import HypheAPIClient

from minet.cli.hyphe.utils import with_hyphe_fatal_errors


@with_hyphe_fatal_errors
def action(cli_args):
    client = HypheAPIClient(cli_args.url)
    corpus = client.corpus(cli_args.corpus, password=cli_args.password)
    corpus.ensure_is_started()

    corpus.call("force_destroy_corpus")

    print("Corpus was successfully destroyed!")
