# =============================================================================
# Minet Youtube Comments CLI Action
# =============================================================================
#
# From a video id, action getting all commments' data using Google's APIs.
#
import time
import sys
import casanova
from tqdm import tqdm
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from ural.youtube import is_youtube_video_id, extract_video_id_from_youtube_url, is_youtube_url

from minet.cli.youtube.utils import seconds_to_midnight_pacific_time
from minet.cli.utils import open_output_file, edit_namespace_with_csv_io, DummyTqdmFile
from minet.utils import create_pool, request_json

URL_TEMPLATE = 'https://www.googleapis.com/youtube/v3/commentThreads?videoId=%(id)s&key=%(key)s&part=snippet,replies&maxResults=100'
URL_PARENTID_TEMPLATE = 'https://youtube.googleapis.com/youtube/v3/comments?part=snippet&parentId=%(id)s&key=%(key)s'

CSV_HEADERS = [
    'comment_id',
    'author_name',
    'author_channel_url',
    'author_channel_id',
    'text',
    'like_count',
    'published_at',
    'updated_at',
    'total_reply',
    'parent_comment_id',
]


def get_data_full(com, top):
    data = []
    snip = ''
    if top:
        data.append(com['topLevelComment']['id'])
        snip = com['topLevelComment']['snippet']
    else:
        data.append(com['id'])
        snip = com['snippet']
    data.append(snip['authorDisplayName'])
    data.append(snip['authorChannelUrl'])
    author = snip.get('authorChannelId', None)
    if author:
        data.append(author['value'])
    else:
        data.append(None)
    data.append(snip['textOriginal'])
    data.append(snip['likeCount'])
    data.append(snip['publishedAt'])
    data.append(snip['updatedAt'])
    if top:
        data.append(com['totalReplyCount'])
        data.append('')
    else:
        data.append(0)
        data.append(snip['parentId'])
    return data


def comments_action(namespace, output_file):

    # Handling output
    output_file = open_output_file(namespace.output)

    # Handling input
    if is_youtube_video_id(namespace.column):
        edit_namespace_with_csv_io(namespace, 'video_id')
    elif is_youtube_url(namespace.column):
        edit_namespace_with_csv_io(namespace, 'video_url')

    # Enricher
    enricher = casanova.enricher(
        namespace.file,
        output_file,
        keep=namespace.select,
        add=CSV_HEADERS
    )

    loading_bar = tqdm(
        desc='Retrieving',
        dynamic_ncols=True,
        unit=' comments',
    )

    http = create_pool()
    error_file = DummyTqdmFile(sys.stderr)

    def make_requests(current_url, http=http):
        return(request_json(http, current_url), current_url)

    for (row, url_id) in enricher.cells(namespace.column, with_rows=True):

        if is_youtube_url(url_id):
            yt_id = extract_video_id_from_youtube_url(url_id)
            if yt_id:
                url = URL_TEMPLATE % {'id': yt_id, 'key': namespace.key}
        elif is_youtube_video_id(url_id):
            url = URL_TEMPLATE % {'id': url_id, 'key': namespace.key}
        else:
            continue
        url_queue = deque([url])
        while len(url_queue) != 0:
            couche = []
            with ThreadPoolExecutor(max_workers=25) as executor:
                time.sleep(0.01)
                couche = executor.map(make_requests, url_queue)
            url_queue = deque()
            for resp in couche:
                ((err, response, result), current_url) = resp
                if err:
                    error_file.write('{} for {}'.format(err, current_url))
                    continue
                elif response.status == 403 and result.get('error').get('errors')[0].get('reason') == 'commentsDisabled':
                    error_file.write('Comments are disabled for {}'.format(current_url))
                    continue
                elif response.status == 403:
                    error_file.write('Running out of API points. You will have to wait until midnight, Pacific time!')
                    time.sleep(seconds_to_midnight_pacific_time())
                    continue
                elif response.status >= 400:
                    error_file.write('Error {} for {}'.format(response.status, current_url))
                    continue
                kind = result.get('kind', None)
                next_page = result.get('nextPageToken', None)
                if next_page:
                    url_next = current_url + '&pageToken=' + next_page
                    url_queue.append(url_next)
                if kind == 'youtube#commentThreadListResponse':
                    # Handling comments pagination
                    items = result.get('items', None)
                    for item in items:
                        snippet = item['snippet']
                        replies = item.get('replies')
                        if replies:
                            # Checking whether youtube's API send a subset of the replies or not
                            if snippet['totalReplyCount'] != len(replies['comments']) and namespace.full:
                                # If we want the replies and those are not all given by the API, we add the URL specific to the topComment
                                # to the queue, and we deal with that topLevelComment
                                new_url = URL_PARENTID_TEMPLATE % {'id': snippet['topLevelComment']['id'], 'key': namespace.key}
                                url_queue.append(new_url)
                                data = get_data_full(snippet, True)
                                enricher.writerow(row, data)
                            else:
                                dataTop = get_data_full(snippet, True)
                                enricher.writerow(row, dataTop)
                                for rep in replies['comments']:
                                    enricher.writerow(row, get_data_full(rep, False))
                        else:
                            # if there is not 'replies' key, it means that the comment we fetch is only a topLevelComment
                            top_comment = get_data_full(snippet, True)
                            enricher.writerow(row, top_comment)
                else:
                    # Handling, commentList, nothing to see here, dealing commments by comments
                    items = result.get('items', None)
                    for item in items:
                        data = get_data_full(item, False)
                        enricher.writerow(row, data)
