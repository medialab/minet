# =============================================================================
# Minet Url Join CLI Action
# =============================================================================
#
# Logic of the `url-join` action.
#
import casanova
from ural.lru import NormalizedLRUTrie

from minet.cli.loading_bar import LoadingBar


def action(cli_args):
    left_reader = casanova.reader(cli_args.input1)
    left_headers = left_reader.fieldnames
    left_idx = None

    if cli_args.select:
        left_idx = left_reader.headers.collect(cli_args.select)
        left_headers = list(cli_args.select)

    # Applying column prefix now
    left_headers = [cli_args.match_column_prefix + h for h in left_headers]

    right_enricher = casanova.enricher(
        cli_args.input2, cli_args.output, add=left_headers
    )

    # First step is to index left file
    trie = NormalizedLRUTrie()

    with LoadingBar(
        title="Indexing first file", unit="lines", total=left_reader.total
    ) as loading_bar:
        for row, cell in left_reader.cells(cli_args.column1, with_rows=True):
            with loading_bar.step():
                if left_idx is not None:
                    row = [row[i] for i in left_idx]

                urls = [cell]

                if cli_args.separator is not None:
                    urls = cell.split(cli_args.separator)

                for url in urls:
                    url = url.strip()

                    # NOTE: should we filter invalid urls here?
                    if url:
                        trie.set(url, row)

    with LoadingBar(
        title="Matching lines in second file", unit="lines", total=right_enricher.total
    ) as loading_bar:
        for row, url in right_enricher.cells(cli_args.column2, with_rows=True):
            with loading_bar.step():
                url = url.strip()

                match = None

                # NOTE: should we filter invalid urls here?
                if url:
                    match = trie.match(url)

                if match is None:
                    right_enricher.writerow(row)
                    continue

                right_enricher.writerow(row, match)
