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

USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"


def fetch_action(namespace):

    HTML_FILES = os.path.join(namespace.storage_location, 'html')
    if not os.path.isdir(HTML_FILES):
        os.makedirs(HTML_FILES)

    # Initializing both reader and writer
    headers, position, source_reader = custom_reader(
        namespace.file, namespace.column)

    monitoring_writer = csv.writer(namespace.monitoring_file)

    # Writing the headers of the monitoring file
    if namespace.monitoring_file.tell() == 0:
        fieldnames = headers + ['status']
        if namespace.id_column is None:
            id_column_name = 'id'
        else:
            id_column_name = namespace.id_column
        fieldnames = [id_column_name] + fieldnames
        monitoring_writer.writerow(fieldnames)

    # Putting the cursor at the beginning of the monitoring file
    namespace.monitoring_file.seek(0, os.SEEK_SET)

    monitoring_reader = csv.reader(namespace.monitoring_file)
    next(monitoring_reader, None)

    http = urllib3.PoolManager()

    line = True

    # Simultaneous loop on source and monitoring csv files
    while line:
        line = next(source_reader, None)
        monitoring_line = next(monitoring_reader, None)

        if (not monitoring_line) and line:
            url = line[position]
            try:
                r = http.request('GET', url, headers={
                                 'user-agent': USER_AGENT}, retries=False)
                html = r.data.decode('utf-8')
                status = r.status
            except Exception as e:
                html = ''
                status = str(e)

            if namespace.id_column is None:
                url_id = uuid.uuid4()
                line = [url_id] + line
            else:
                id_position = headers.index(id_column_name)
                url_id = line[id_position]
                line = [url_id] + line

            with open(os.path.join(HTML_FILES, str(url_id) + '.html'), "w") as text_file:
                text_file.write(html)
            line = line + [status]
            monitoring_writer.writerow(line)
    # yield html
