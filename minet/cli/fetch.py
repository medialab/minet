# =============================================================================
# Minet Fetch CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and fetching the urls found
# in the given column. This is done in a respectful multithreaded fashion to
# optimize both running time & memory.
#
import os
from tqdm import tqdm
from quenouille import imap

from minet.cli.utils import custom_reader


def fetch_action(namespace):
    input_headers, pos, reader = custom_reader(namespace.file, namespace.column)

    # First we need to create the relevant directory
    os.makedirs(namespace.output_dir, exist_ok=True)

