# =============================================================================
# Minet Facebook CLI Action
# =============================================================================
#
# Logic of the Facebook share count fetching action.
#

import os
import csv
from minet.cli.utils import custom_reader
from minet.facebook import fetch_share_count

from progress.bar import FillingSquaresBar


def facebook_action(namespace):

    bar = FillingSquaresBar('Fetching FB shares')

    headers, position, reader = custom_reader(namespace.file, namespace.column)

    headers.append("facebook_share_count")
    writer = csv.writer(namespace.output)
    writer.writerow(headers)

    for line in reader:
        bar.next()
        url = line[position]
        line.append(fetch_share_count(url))
        writer.writerow(line)
    bar.goto(100)
    bar.finish()
