# =============================================================================
# Minet Facebook CLI Action
# =============================================================================
#
# Logic of the Facebook share count fetching action.
#

import os
import csv
import sys
from minet.cli.utils import custom_reader
from minet.facebook import fetch_share_count

from progress.bar import FillingSquaresBar


def facebook_action(namespace):

    headers, position, reader = custom_reader(namespace.file, namespace.column)

    headers.append("facebook_share_count")
    writer = csv.writer(namespace.output)
    writer.writerow(headers)

    if namespace.output == sys.stdout:
        for line in reader:
            url = line[position]
            line.append(fetch_share_count(url))
            writer.writerow(line)

    else:
        bar = FillingSquaresBar('Fetching FB shares')

        for line in reader:
            bar.next()
            url = line[position]
            line.append(fetch_share_count(url))
            writer.writerow(line)
        bar.goto(100)
        bar.finish()
