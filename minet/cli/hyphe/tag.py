# =============================================================================
# Minet Hyphe Tag CLI Action
# =============================================================================
#
# Logic of the `hyphe tag` action.
#
import casanova

from minet.cli.loading_bar import LoadingBar
from minet.cli.hyphe.utils import with_hyphe_fatal_errors
from minet.cli.exceptions import InvalidArgumentsError
from minet.hyphe import HypheAPIClient
from minet.hyphe.exceptions import HypheRequestFailError


@with_hyphe_fatal_errors
def action(cli_args):
    reader = casanova.reader(cli_args.data, total=cli_args.total)
    headers = reader.headers

    if cli_args.webentity_id_column not in headers:
        raise InvalidArgumentsError(
            "%s column does not exists in given CSV file" % cli_args.webentity_id_column
        )

    tag_pos_map = {}

    for tag_column in cli_args.tag_columns:
        if tag_column not in headers:
            raise InvalidArgumentsError(
                "%s column does not exists in given CSV file" % tag_column
            )

        tag_pos_map[tag_column] = headers[tag_column]

    client = HypheAPIClient(cli_args.url)
    corpus = client.corpus(cli_args.corpus, password=cli_args.password)
    corpus.ensure_is_started()

    with LoadingBar(
        title="Tagging web entities", unit="webentity", total=reader.total
    ) as loading_bar:
        for row, webentity_id in reader.cells(
            cli_args.webentity_id_column, with_rows=True
        ):
            with loading_bar.step():
                webentity_id = webentity_id.strip()

                if not webentity_id:
                    continue

                try:
                    webentity_id = int(webentity_id)
                except ValueError:
                    loading_bar.print('invalid webentity id "%s"' % webentity_id)
                    continue

                for tag_name, tag_pos in tag_pos_map.items():
                    tag_values = row[tag_pos].strip()

                    if not tag_values:
                        continue

                    tag_values = tag_values.split(cli_args.separator)

                    for tag_value in tag_values:
                        if not tag_value:
                            continue

                        try:
                            corpus.call(
                                "store.add_webentity_tag_value",
                                webentity_id=webentity_id,
                                namespace="USER",
                                category=tag_name,
                                value=tag_value,
                            )
                        except HypheRequestFailError as e:
                            if "could not retrieve WebEntity with id" in str(e):
                                loading_bar.print(
                                    'unkown webentity with id "%s"' % webentity_id
                                )
                                break
                            else:
                                raise
