# =============================================================================
# Minet Url Join CLI Action
# =============================================================================
#
# Logic of the `url-join` action.
#
import casanova
from ural.lru import NormalizedLRUTrie

from minet.cli.utils import LoadingBar


def url_join_action(cli_args):
    left_reader = casanova.reader(cli_args.file1)
    left_headers = left_reader.fieldnames
    left_idx = None

    if cli_args.select:
        left_idx = left_reader.headers.collect(cli_args.select)
        left_headers = list(cli_args.select)

    # Applying column prefix now
    left_headers = [cli_args.match_column_prefix + h for h in left_headers]

    right_enricher = casanova.enricher(
        cli_args.file2,
        cli_args.output,
        add=left_headers
    )

    loading_bar = LoadingBar(
        desc='Indexing left file',
        unit='line'
    )

    # First step is to index left file
    trie = NormalizedLRUTrie()

    for row, cell in left_reader.cells(cli_args.column1, with_rows=True):
        loading_bar.update()

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

    loading_bar.close()

    loading_bar = LoadingBar(
        desc='Matching right file',
        unit='line'
    )

    for row, url in right_enricher.cells(cli_args.column2, with_rows=True):
        loading_bar.update()

        url = url.strip()

        match = None

        # NOTE: should we filter invalid urls here?
        if url:
            match = trie.match(url)

        if match is None:
            right_enricher.writerow(row)
            continue

        right_enricher.writerow(row, match)
