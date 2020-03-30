# =============================================================================
# Minet Youtube Comments CLI Action
# =============================================================================
#
# From a video id, action getting all commments' data using Google's APIs.
#
import time
import csv
from tqdm import tqdm
from minet.cli.youtube.utils import seconds_to_midnight_pacific_time
from minet.cli.utils import die, open_output_file
from minet.utils import create_pool, request_json

URL_TEMPLATE = 'https://www.googleapis.com/youtube/v3/commentThreads?videoId=%(id)s&key=%(key)s&part=snippet,replies&maxResults=100'

CSV_HEADERS = [
    'video_id',
    'comment_id',
    'author_name',
    'author_channel_url',
    'author_channel_id',
    'text',
    'like_count',
    'published_at',
    'updated_at',
    'total_reply',
    'reply_to'
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
            video_id,
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


def comments_action(namespace, output_file):

    output_file = open_output_file(namespace.output)

    writer = csv.writer(output_file)
    writer.writerow(CSV_HEADERS)

    loading_bar = tqdm(
        desc='Retrieving',
        dynamic_ncols=True,
        unit=' comments',
    )

    http = create_pool()

    url = URL_TEMPLATE % {'id': namespace.id, 'key': namespace.key}
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
            writer.writerow(comment)
