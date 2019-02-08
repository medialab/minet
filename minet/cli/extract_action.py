# =============================================================================
# Minet Extract Content CLI Action
# =============================================================================
#
# Logic of the extract action.
#
from minet.cli.utils import custom_reader
from minet.cli.fetch_action import fetch_action
from minet.extract import extract_content


def extract_action(namespace):
    # fetch_action(namespace)
    extract_content(namespace.storage_location, namespace.monitoring_file.name)
