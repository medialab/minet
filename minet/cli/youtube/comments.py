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
    'video_id',
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


def seconds_to_midnight_pacific_time():
    now_utc = timezone('utc').localize(datetime.utcnow())
    pacific_time = now_utc.astimezone(timezone('US/Pacific')).replace(tzinfo=None)
    midnight_pacific = datetime.combine(pacific_time, datetime.min.time())
    return (midnight_pacific - pacific_time).seconds


def get_replies(data_replies):

    data = []
    for item in data_replies:

        snippet = item['snippet']
        video_id = ''
        comment_id = item['id']
        author_name = snippet['authorDisplayName']
        author_channel_url = snippet['authorChannelUrl']
        author_channel_id = snippet['authorChannelId']['value']
        text = snippet['textOriginal']
        like_count = snippet['likeCount']
        publisehd_at = snippet['publishedAt']
        updated_at = snippet['updatedAt']
        total_reply = 0
        reply_to = snippet['parentId']

        data.append([
            video_id,
            comment_id,
            author_name,
            author_channel_url,
            author_channel_id,
            text,
            like_count,
            publisehd_at,
            updated_at,
            total_reply,
            reply_to
        ])

    return data


def get_data(data_json):

    data = []
    next_page = ''

    next_page = data_json.get('nextPageToken', None)

    for item in data_json['items']:

        snippet = item['snippet']

        top_comment = snippet['topLevelComment']
        total_reply = snippet['totalReplyCount']

        if total_reply > 0:
            replies = item['replies']
            data += get_replies(replies['comments'])

        info = top_comment['snippet']

        video_id = snippet['videoId']
        comment_id = top_comment['id']
        author_name = info['authorDisplayName']
        author_channel_url = info['authorChannelUrl']
        author_channel_id = info['authorChannelId']['value']
        text = info['textOriginal']
        like_count = info['likeCount']
        publisehd_at = info['publishedAt']
        updated_at = info['updatedAt']
        total_reply = total_reply
        reply_to = ''

        data.append([
            video_id,
            comment_id,
            author_name,
            author_channel_url,
            author_channel_id,
            text,
            like_count,
            publisehd_at,
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
            time.sleep(time_in_seconds())
        elif response.status >= 400:
            die(response.status)

        next_page, data = get_data(result)
        all_data += data

    for comment in all_data:
        loading_bar.update()
        writer.writerow(comment)
