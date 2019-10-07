# =============================================================================
# Minet Url Join CLI Action
# =============================================================================
#
# Logic of the `url-join` action.
#
import csv
from ural import LRUTrie
from tqdm import tqdm

from minet.cli.utils import custom_reader, DummyTqdmFile


def url_join_action(namespace):

    left_headers, left_pos, left_reader = custom_reader(namespace.file1, namespace.column1)
    right_headers, right_pos, right_reader = custom_reader(namespace.file2, namespace.column2)

    if namespace.select:
        left_headers = namespace.select.split(',')
        selected_pos = [left_headers.index(h) for h in left_headers]

    if namespace.output is None:
        output_file = DummyTqdmFile()
    else:
        output_file = open(namespace.output, 'w')

    output_writer = csv.writer(output_file)
    output_writer.writerow(right_headers + left_headers)

    loading_bar = tqdm(
        desc='Indexing left file',
        dynamic_ncols=True,
        unit=' lines'
    )

    # First step is to index left file
    trie = LRUTrie(strip_trailing_slash=True)

    for line in left_reader:
        url = line[left_pos].strip()

        if namespace.select:
            line = [line[p] for p in selected_pos]

        trie.set(url, line)

        loading_bar.update()

    loading_bar.close()

    loading_bar = tqdm(
        desc='Matching right file',
        dynamic_ncols=True,
        unit=' lines'
    )

    for line in right_reader:
        url = line[right_pos].strip()

        match = None

        if url:
            match = trie.match(url)

        loading_bar.update()

        if match is None:
            output_writer.writerow(line)
            continue

        line.extend(match)
        output_writer.writerow(line)

    output_file.close()
