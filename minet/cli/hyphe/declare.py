# =============================================================================
# Minet Hyphe Declare CLI Action
# =============================================================================
#
# Logic of the `hyphe declare` action.
#
import casanova
from urllib.parse import unquote

from minet.cli.loading_bar import LoadingBar
from minet.cli.exceptions import InvalidArgumentsError
from minet.cli.hyphe.utils import with_hyphe_fatal_errors
from minet.hyphe import HypheAPIClient
from minet.hyphe.exceptions import HypheRequestFailError


def extract_tags(row, tag_pos_list):
    tags = {}

    for name, pos in tag_pos_list:
        cell_value = row[pos]

        if not cell_value:
            continue

        # TODO: hyphe tag serialization is not bijective
        tags[name] = cell_value.split("|")

    return {"USER": tags}


@with_hyphe_fatal_errors
def action(cli_args):
    reader = casanova.reader(cli_args.webentities, total=cli_args.total)
    headers = reader.headers

    name_pos = headers.get("NAME")
    homepage_pos = headers.get("HOME PAGE")
    prefixes_pos = headers.get("PREFIXES AS LRU")
    status_pos = headers.get("STATUS")
    startpages_pos = headers.get("START PAGES")

    tag_pos_list = [
        (name.split("(TAGS)", 1)[0].strip(), pos)
        for name, pos in headers
        if name.endswith("(TAGS)")
    ]

    if (
        name_pos is None
        or prefixes_pos is None
        or homepage_pos is None
        or status_pos is None
        or startpages_pos is None
    ):
        raise InvalidArgumentsError(
            "input csv file is not a valid hyphe webentities export"
        )

    client = HypheAPIClient(cli_args.url)
    corpus = client.corpus(cli_args.corpus, password=cli_args.password)

    corpus.ensure_is_started()

    with LoadingBar(
        title="Declaring web entities", unit="webentities", total=reader.total
    ) as loading_bar:
        for row in reader:
            with loading_bar.step():
                startpages_cell = row[startpages_pos]

                name = row[name_pos]

                # TODO: bug on hyphe's side
                if "h:localhost|" in row[prefixes_pos]:
                    loading_bar.print("Dropping %s because of localhost issue" % name)
                    continue

                homepage = row[homepage_pos]
                prefixes = row[prefixes_pos].split(" ")
                startpages = startpages_cell.split(" ") if startpages_cell else []
                startpages = list(
                    set(startpages)
                )  # TODO: dedupe because of hyphe issues
                tags = extract_tags(row, tag_pos_list)

                # 1. Declaring the entities
                result = corpus.call(
                    "store.declare_webentity_by_lrus",
                    list_lrus=prefixes,
                    name=name,
                    status=row[status_pos],
                    lruVariations=False,
                    startpages=startpages,
                    tags=tags,
                )

                webentity_id = result["result"]["id"]

                # 2. Setting the homepage
                try:
                    corpus.call(
                        "store.set_webentity_homepage",
                        webentity_id=webentity_id,
                        homepage=unquote(
                            homepage
                        ),  # TODO: drop unquote, linked to hyphe issue #447
                    )
                except HypheRequestFailError as e:
                    if "belong" in str(e):
                        loading_bar.print(
                            "Homepage error with %s %s" % (name, homepage)
                        )
                    else:
                        raise
