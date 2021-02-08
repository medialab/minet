# =============================================================================
# Minet Url Join CLI Action
# =============================================================================
#
# Logic of the `url-join` action.
#
import csv
import casanova
from casanova.reader import collect_column_indices
from ural.lru import NormalizedLRUTrie
from tqdm import tqdm

from minet.cli.utils import open_output_file


def url_join_action(namespace):
    right_reader = casanova.reader(namespace.file2)
    left_reader = casanova.reader(
        namespace.file1,
        namespace.output
    )

    output_file = open_output_file(namespace.output)
    output_writer = csv.writer(output_file)

    left_headers = left_reader.fieldnames
    left_indices = None

    if namespace.select is not None:
        selected = namespace.select.split(',')
        left_headers = [h for h in left_headers if h in selected]
        left_indices = collect_column_indices(left_reader.pos, left_headers)

    empty = [''] * len(left_headers)

    output_writer.writerow(right_reader.fieldnames + left_headers)

    loading_bar = tqdm(
        desc='Indexing left file',
        dynamic_ncols=True,
        unit=' lines'
    )

    # First step is to index left file
    trie = NormalizedLRUTrie()

    def add_url(u, row):
        u = u.strip()

        if u:
            trie.set(u, row)

    for row, url in left_reader.cells(namespace.column1, with_rows=True):
        if left_indices is not None:
            row = [row[i] for i in left_indices]

        if namespace.separator is not None:
            for u in url.split(namespace.separator):
                add_url(u, row)
        else:
            add_url(u, row)

        loading_bar.update()

    loading_bar.close()

    loading_bar = tqdm(
        desc='Matching right file',
        dynamic_ncols=True,
        unit=' lines'
    )

    for row, url in right_reader.cells(namespace.column2, with_rows=True):
        url = url.strip()

        match = None

        if url:
            match = trie.match(url)

        loading_bar.update()

        if match is None:
            output_writer.writerow(row + empty)
            continue

        row.extend(match)
        output_writer.writerow(row)

    output_file.close()
