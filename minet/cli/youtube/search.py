# =============================================================================
# Minet Youtube Search CLI Action
# =============================================================================
#
# From a key-word, action getting all video's related to that keyword data using Google's APIs.
#
import time
import sys
import casanova
from tqdm import tqdm
from minet.cli.youtube.utils import seconds_to_midnight_pacific_time
from minet.cli.utils import die, open_output_file, edit_namespace_with_csv_io, DummyTqdmFile
from minet.utils import create_pool, request_json

URL_TEMPLATE = 'https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=100&q=%(subject)s&type=video&order=%(order)s&key=%(key)s'

CSV_HEADERS = [
    'video_id',
    'channel_title',
    'channel_id',
    'title',
    'description',
    'published_at',
]


def get_data(video):
    data_all = []
    nextpage = video.get('nextPageToken', None)
    items = video.get('items')
    for item in items:
        data = []
        snip = item.get('snippet')
        data.append(item.get('id')['videoId'])
        data.append(snip['channelTitle'])
        data.append(snip['channelId'])
        data.append(snip['title'])
        data.append(snip['description'])
        data.append(snip['publishedAt'])
        data_all.append(data)
    return nextpage, data_all


def search_action(namespace, output_file):

    # Handling output
    output_file = open_output_file(namespace.output)

    edit_namespace_with_csv_io(namespace, 'keyword')

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        keep=namespace.select,
        add=CSV_HEADERS
    )

    loading_bar = tqdm(
        desc='Retrieving',
        dynamic_ncols=True,
        unit='videos',
    )
    http = create_pool()
    error_file = DummyTqdmFile(sys.stderr)
    limit = namespace.limit

    for (row, keyword) in enricher.cells(namespace.column, with_rows=True):
        url = URL_TEMPLATE % {'subject': keyword, 'order': namespace.order, 'key': namespace.key}
        next_page = True
        while next_page:
            if next_page is True:
                err, response, result = request_json(http, url)
            else:
                url_next = url + '&pageToken=' + next_page
                err, response, result = request_json(http, url_next)
            if err:
                die(err)
            elif response.status == 403:
                error_file.write('Running out of API points. You will have to wait until midnight, Pacific time!')
                time.sleep(seconds_to_midnight_pacific_time())
                continue
            elif response.status >= 400:
                die(response.status)
            next_page, data_l = get_data(result)
            for data in data_l:
                if limit is not(None):
                    if limit == 0:
                        return True
                    else:
                        limit -= 1
                        enricher.writerow(row, data)
                else:
                    enricher.writerow(row, data)
