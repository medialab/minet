# =============================================================================
# Minet Fetch HTML CLI Action
# =============================================================================
#
# Logic of the fetch HTML action.
#
import csv
import sys
import os
import urllib3
urllib3.disable_warnings()
import uuid

from minet.cli.utils import custom_reader
# from minet.fetch import fetch


def fetch_action(namespace):

    HTML_FILES = os.path.join(namespace.storage_location, 'html')
    if not os.path.isdir(HTML_FILES):
        os.makedirs(HTML_FILES)

    headers, position, source_reader = custom_reader(
        namespace.file, namespace.column)

    monitoring_writer = csv.writer(namespace.monitoring_file)

    # Writing the headers of the monitoring file
    if namespace.monitoring_file.tell() == 0:
        fieldnames = headers + ['status']
        monitoring_writer.writerow(fieldnames)

    # Putting the cursor at the beginning of the monitoring file
    namespace.monitoring_file.seek(0, os.SEEK_SET)

    monitoring_reader = csv.reader(namespace.monitoring_file)

    http = urllib3.PoolManager()

    line = True

    # Simultaneous loop on source and monitoring csv files
    while line:
        line = next(source_reader, None)
        monitoring_line = next(monitoring_reader, None)

        if (not monitoring_line) and line:
            url = line[position]
            print('Fetching', url)
            r = http.request('GET', url)
            html = r.data.decode('utf-8')

            if namespace.id_column is None:
                url_id = uuid.uuid4()
            else:
                id_position = headers.index(namespace.id_column)
                url_id = line[id_position]

            with open(os.path.join(HTML_FILES, str(url_id) + '.html'), "w") as text_file:
                text_file.write(html)
            line = line + [r.status]
            monitoring_writer.writerow(line)

        # yield html
