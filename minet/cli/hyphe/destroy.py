# =============================================================================
# Minet Hyphe Destroy CLI Action
# =============================================================================
#
# Logic of the `hyphe destroy` action.
#
from minet.cli.utils import die
from minet.hyphe import HypheAPIClient
from minet.hyphe.exceptions import HypheCorpusAuthenticationError


def hyphe_destroy_action(cli_args):
    client = HypheAPIClient(cli_args.url)
    corpus = client.corpus(cli_args.corpus, password=cli_args.password)

    try:
        corpus.ensure_is_started()
    except HypheCorpusAuthenticationError:
        die(
            [
                'Wrong password for the "%s" corpus!' % cli_args.corpus,
                "Don't forget to provide a password for this corpus using --password",
            ]
        )

    err, _ = corpus.call("force_destroy_corpus")

    if err:
        raise err

    print("Corpus was successfully destroyed!")
