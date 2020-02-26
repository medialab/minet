# =============================================================================
# Minet Youtube Videos CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving metadata about
# the given Youtube videos using Google's APIs.
#
from tqdm import tqdm

from minet.cli.utils import CSVEnricher

REPORT_HEADERS = []


def videos_action(namespace, output_file):
    enricher = CSVEnricher(
        namespace.file,
        namespace.column,
        output_file,
        report_headers=REPORT_HEADERS,
        select=namespace.select.split(',') if namespace.select else None
    )

    loading_bar = tqdm(
        desc='Retrieving',
        dynamic_ncols=True,
        unit=' videos',
    )

    for line in enricher:

        loading_bar.update()

        enricher.write(
            line,
            []
        )
