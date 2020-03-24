# =============================================================================
# Minet Youtube Comments CLI Action
# =============================================================================
#
# From a video id, action getting all commments' data using Google's APIs.
#
import time
import csv
from pytz import timezone
from datetime import datetime
from tqdm import tqdm
from minet.cli.utils import die, open_output_file
from minet.utils import create_pool, request_json

URL_TEMPLATE = 'https://www.googleapis.com/youtube/v3/commentThreads?videoId=%(id)s&key=%(key)s&part=snippet,replies&maxResults=100'

CSV_HEADERS = [
    'comment_id',
    'author_name',
    'author_channel_url',
    'author_channel_id',
    'text',
    'like_count',
    'publisehd_at',
    'updated_at',
    'total_reply',
    'reply_to'
]


def time_in_seconds():
    now_utc = timezone('utc').localize(datetime.utcnow())
    pacific_time = now_utc.astimezone(timezone('US/Pacific')).replace(tzinfo=None)
    midnight_pacific = datetime.combine(pacific_time, datetime.min.time())
    return (midnight_pacific - pacific_time).seconds


def get_replies(data_replies, data):

    for item in data_replies:

        snippet = item['snippet']

        data.append({
            'comment_id': item['id'],
            'author_name': snippet['authorDisplayName'],
            'author_channel_url': snippet['authorChannelUrl'],
            'author_channel_id': snippet['authorChannelId']['value'],
            'text': snippet['textOriginal'],
            'like_count': snippet['likeCount'],
            'publisehd_at': snippet['publishedAt'],
            'updated_at': snippet['updatedAt'],
            'total_reply': None,
            'reply_to': snippet['parentId']
        })

    return data


def get_data(data_json, data):

    nextPage = ''

    for key in data_json.keys():
        if key == 'nextPageToken':
            nextPage = data_json['nextPageToken']

    for item in data_json['items']:

        snippet = item['snippet']

        top_comment = snippet['topLevelComment']
        total_reply = snippet['totalReplyCount']

        if total_reply > 0:
            replies = item['replies']
            data_replies = get_replies(replies['comments'], data)

        info = top_comment['snippet']

        data.append({
            'comment_id': top_comment['id'],
            'author_name': info['authorDisplayName'],
            'author_channel_url': info['authorChannelUrl'],
            'author_channel_id': info['authorChannelId']['value'],
            'text': info['textOriginal'],
            'like_count': info['likeCount'],
            'publisehd_at': info['publishedAt'],
            'updated_at': info['updatedAt'],
            'total_reply': total_reply,
            'reply_to': None
        })

    return nextPage, data


def comments_action(namespace, output_file):

    output_file = open_output_file(namespace.output)

    writer = csv.writer(output_file)
    writer.writerow(CSV_HEADERS)

    loading_bar = tqdm(
        desc='Retrieving',
        dynamic_ncols=True,
        unit=' comments',
    )

    def format_csv_row(comments):
        row = []

        for key in CSV_HEADERS:
            row.append(comments[key] or '')

        return row

    http = create_pool()

    url = URL_TEMPLATE % {'id': namespace.id, 'key': namespace.key}
    err, response, result = request_json(http, url)

    if err:
        die(err)
    elif response.status == 403:
        time.sleep(time_in_seconds())
    elif response.status >= 400:
        die(response.status)

    all_data = []
    nextPage, all_data = get_data(result, all_data)

    while nextPage:
        url_next = url + '&pageToken=' + nextPage
        err, response, result = request_json(http, url_next)

        if err:
            die(err)
        elif response.status == 403:
            time.sleep(time_in_seconds())
        elif response.status >= 400:
            die(response.status)

        nextPage, all_data = get_data(result, all_data)

    for comment in all_data:
        loading_bar.update()
        writer.writerow(format_csv_row(comment))
