# =============================================================================
# Minet Youtube Comments CLI Action
# =============================================================================
#
# From a video id, action getting all commments' data using Google's APIs.
#
import casanova
from tqdm import tqdm
from collections import deque
import time
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
    'Parent_com_id',
]


def get_data(data_json):
    data = []
    data_replies = []
    next_page = data_json.get('nextPageToken', None)
    all_items = data_json.get('items', None)
    is_reply = False

    if not all_items:
        all_items = data_json.get('comments', None)
        is_reply = True

    for item in all_items:

        comment_id = item.get('id', None)
        snippet = item['snippet']

        if is_reply:
            comment_data = snippet
        else:
            replies = item.get('replies', None)

            if replies:
                _, data_replies = get_data(replies)
                data.extend(data_replies)

            top_comment = snippet.get('topLevelComment', None)
            comment_data = top_comment.get('snippet', None)

        total_reply = snippet.get('totalReplyCount', None)
        author_name = comment_data['authorDisplayName']
        author_channel_url = comment_data['authorChannelUrl']
        author_channel_id = comment_data['authorChannelId']['value']
        video_id = comment_data['videoId']
        text = comment_data['textOriginal']
        like_count = comment_data['likeCount']
        published_at = comment_data['publishedAt']
        updated_at = comment_data['updatedAt']
        reply_to = comment_data.get('parentId', None)

        data.append([
            comment_id,
            author_name,
            author_channel_url,
            author_channel_id,
            text,
            like_count,
            published_at,
            updated_at,
            total_reply,
            reply_to
        ])

    return next_page, data


def get_data_full(Com, top):
    data = []
    snip = ''
    if top:
        data.append(Com['topLevelComment']['id'])
        snip = Com['topLevelComment']['snippet']
    else:
        data.append(Com['id'])
        snip = Com['snippet']
    data.append(snip['authorDisplayName'])
    data.append(snip['authorChannelUrl'])
    data.append(snip['authorChannelId']['value'])
    data.append(snip['textOriginal'])
    data.append(snip['likeCount'])
    data.append(snip['publishedAt'])
    data.append(snip['updatedAt'])
    if top:
        data.append(Com['totalReplyCount'])
        data.append(None)
    else:
        data.append(None)
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
        if namespace.full:
            url_queue = deque([(url)])

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
                commentThread = False
                kind = result.get('kind', None)
                # Handling comments pagination
                if kind == 'youtube#commentThreadListResponse':
                    commentThread = True
                    next_page = result.get('nextPageToken', None)
                    if next_page:
                        url_next = current_url + '&pageToken=' + next_page
                        url_queue.append(url_next)
                # Handling CommentThreadList urls
                if commentThread:
                    items = result.get('items', None)
                    for item in items:
                        snippet = item['snippet']
                        try:
                            replies = item['replies']
                            # Checking whether youtube's API send a subset of the replies or not
                            if snippet['totalReplyCount'] == len(replies['comments']):
                                # if all the comments are properly given, we first write the ToplevelComment
                                top_comment = get_data_full(snippet, True)
                                enricher.writerow(row, top_comment)
                                liste_com = replies['comments']
                                # and the replies to that specific comment
                                for x in liste_com:
                                    enricher.writerow(row, get_data_full(x, False))
                            else:
                                # If all the comments are not given by the API, we add the URL specific to the topComment
                                # to the queue, and we deal with that topLevelComment
                                new_url = URL_PARENTID_TEMPLATE % {'id': snippet['topLevelComment']['id'], 'key': namespace.key}
                                url_queue.append(new_url)
                                data = get_data_full(snippet, True)
                                enricher.writerow(row, data)
                        except KeyError:
                            # if there is not 'replies' key, it means that the comment we fetch is only a topLevelComment
                            top_comment = get_data_full(snippet, True)
                            enricher.writerow(row, top_comment)
                else:
                    # Handling, commentList, nothing to see here, dealing commments by comments
                    items = result.get('items', None)
                    for item in items:
                        data = get_data_full(item, False)
                        enricher.writerow(row, data)
        else:
            # Here we are not fetching all the commentaries
            next_page = True
            all_data = []

            while next_page:

                if next_page is True:
                    err, response, result = request_json(http, url)
                else:
                    url_next = url + '&pageToken=' + next_page
                    err, response, result = request_json(http, url_next)

                if err:
                    die(err)
                elif response.status == 403:
                    time.sleep(seconds_to_midnight_pacific_time())
                    continue
                elif response.status >= 400:
                    die(response.status)

                next_page, data = get_data(result)

                for comment in data:
                    loading_bar.update()
                    enricher.writerow(row, comment)
