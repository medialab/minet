# =============================================================================
# Minet Hyphe Dump CLI Action
# =============================================================================
#
# Logic of the `hyphe dump` action.
#
import casanova

from minet.cli.utils import die, LoadingBar
from minet.cli.exceptions import InvalidArgumentsError
from minet.hyphe import HypheAPIClient
from minet.hyphe.exceptions import HypheCorpusAuthenticationError


def hyphe_declare_action(cli_args):
    reader = casanova.reader(cli_args.webentities, total=cli_args.total)
    headers = reader.headers

    name_pos = headers.get('NAME')
    homepage_pos = headers.get('HOMEPAGE')
    prefixes_pos = headers.get('PREFIXES AS LRU')
    status_pos = headers.get('STATUS')
    startpages_pos = headers.get('START PAGES')

    if (
        name_pos is None or
        prefixes_pos is None or
        homepage_pos is None or
        status_pos is None or
        startpages_pos is None
    ):
        raise InvalidArgumentsError('input csv file is not a valid hyphe webentities export')

    client = HypheAPIClient(cli_args.url)
    corpus = client.corpus(cli_args.corpus, password=cli_args.password)

    try:
        corpus.ensure_is_started()
    except HypheCorpusAuthenticationError:
        die([
            'Wrong password for the "%s" corpus!' % cli_args.corpus,
            'Don\'t forget to provide a password for this corpus using --password'
        ])

    loading_bar = LoadingBar(
        desc='Declaring web entities',
        unit='webentity',
        unit_plural='webentities',
        total=reader.total
    )

    for row in reader:
        loading_bar.update()

        prefixes = row[prefixes_pos].split(' ')
        startpages = row[startpages_pos].split(' ')

        # 1. Declaring the entities
        err, result = corpus.call(
            'store.declare_webentity_by_lrus',
            list_lrus=prefixes,
            name=row[name_pos],
            status=row[status_pos],
            lruVariations=False,
            startpages=startpages
        )

        # TODO: tags

        if err:
            raise err

        webentity_id = result['result']['id']

        # 2. Setting the homepage
        client.call(
            'set_webentity_homepage',
            webentity_id=webentity_id,
            homepage=row[homepage_pos]
        )
