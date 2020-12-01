# =============================================================================
# Minet Youtube Comments CLI Action
# =============================================================================
#
# From a video id, action getting all commments' data using Google's APIs.
#
import time
import casanova
from tqdm import tqdm
from collections import deque
from ural.youtube import is_youtube_video_id, extract_video_id_from_youtube_url, is_youtube_url

from minet.cli.youtube.utils import seconds_to_midnight_pacific_time
from minet.cli.utils import die, open_output_file, edit_namespace_with_csv_io
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
    data.append(snip['authorChannelId']['value'])
    data.append(snip['textOriginal'])
    data.append(snip['likeCount'])
    data.append(snip['publishedAt'])
    data.append(snip['updatedAt'])
    if top:
        data.append(com['totalReplyCount'])
        data.append("")
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

    for (row, url_id) in enricher.cells(namespace.column, with_rows=True):

        if is_youtube_url(url_id):
            url = URL_TEMPLATE % {'id': extract_video_id_from_youtube_url(url_id), 'key': namespace.key}
        else:
            url = URL_TEMPLATE % {'id': url_id, 'key': namespace.key}
        # FULL commentaries
        # if namespace.full:
        url_queue = deque([url])

        while len(url_queue) != 0:
            current_url = url_queue.popleft()
            err, response, result = request_json(http, current_url)
            if err:
                die(err)
            elif response.status == 403:
                time.sleep(seconds_to_midnight_pacific_time())
                continue
            elif response.status >= 400:
                die(response.status)
            kind = result.get('kind', None)
            if kind == 'youtube#commentThreadListResponse':
                # Handling comments pagination
                next_page = result.get('nextPageToken', None)
                if next_page:
                    url_next = current_url + '&pageToken=' + next_page
                    url_queue.append(url_next)
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
