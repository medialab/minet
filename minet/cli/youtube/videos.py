# =============================================================================
# Minet Youtube Videos CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving metadata about
# the given Youtube videos using Google's APIs.
#
import time
import datetime
import pytz
from pytz import timezone
from datetime import date, datetime, timedelta
from tqdm import tqdm
from minet.cli.utils import CSVEnricher, die
from minet.utils import create_pool, request_json
from ural.youtube import (
    extract_video_id_from_youtube_url,
    is_youtube_video_id,
    is_youtube_url
)

URL_TEMPLATE = 'https://www.googleapis.com/youtube/v3/videos?id=%(list_id)s&key=%(key)s&part=snippet,statistics'

REPORT_HEADERS = [
    'video_id',
    'published_at',
    'channel_id',
    'title',
    'description',
    'channel_title',
    'view_count',
    'like_count',
    'dislike_count',
    'favorite_count',
    'comment_count',
    'no_stat_likes'
]


def wait():
    now_utc = datetime.utcnow()
    # PST
    result = now_utc + timedelta(hours=-7)
    midnight_pacific = datetime.combine(result, datetime.min.time())
    return (midnight_pacific - result).seconds


def get_data(data_json):
    data = []
    snippet = {}
    stat = {}
    elements = []
    no_stat_likes = ''

    elements = data_json['items']

    for el in elements:

        video_id = el['id']
        snippet = el['snippet']
        stat = el['statistics']

        published_at = snippet['publishedAt']
        channel_id = snippet['channelId']
        channel_title = snippet['channelTitle']
        title = snippet['title']
        description = snippet['description']

        view_count = stat.get('viewCount', None)
        like_count = stat.get('likeCount', None)
        dislike_count = stat.get('dislikeCount', None)
        favorite_count = stat.get('favoriteCount', None)
        comment_count = stat.get('commentCount', None)

        if not like_count:
            no_stat_likes = '1'

        data.append([video_id, published_at, channel_id, title, description, channel_title, view_count, like_count, dislike_count, favorite_count, comment_count, no_stat_likes])

    return data


def gen_chunks(enricher):
    chunk = []

    for num, line in enumerate(enricher):

        url_data = line[enricher.pos]

        if len(chunk) == 50:
            yield chunk
            chunk.clear()

        if is_youtube_video_id(url_data):
            video_id = url_data

        elif is_youtube_url(url_data):
            video_id = extract_video_id_from_youtube_url(url_data)

        chunk.append((video_id, line))

    yield chunk


def videos_action(namespace, output_file):

    enricher = CSVEnricher(
        namespace.file,
        namespace.column,
        output_file,
        report_headers=REPORT_HEADERS,
        select=namespace.select.split(',') if namespace.select else None
    )

    loading_bar = tqdm(
        desc='Retrieving',
        dynamic_ncols=True,
        unit=' videos',
    )

    for chunk in gen_chunks(enricher):

        all_ids = []
        for i in chunk:
            if i[0]:
                all_ids.append(i[0])

        list_id = ",".join(all_ids)

        url = URL_TEMPLATE % {'list_id': list_id, 'key': namespace.key}
        http = create_pool()
        err, response, result = request_json(http, url)

        if err:
            die(err)
        elif response.status == 403:
            time.sleep(wait())
        elif response.status >= 400:
            die(response.status)

        data = get_data(result)

        id_available = []
        for sub_list in data:
            id_available.append(sub_list[0])

        not_available = list(set(all_ids).difference(set(id_available)))

        loading_bar.update(len(chunk))

        rank = 0
        line_empty = ['' for i in range(len(REPORT_HEADERS) - 1)]

        for line in chunk:
            if not line[0]:
                enricher.write_empty(line[1])

            elif line[0] in not_available:
                line_empty.insert(0, line[0])
                enricher.write(line[1], line_empty)
                line_empty.pop(0)

            else:
                enricher.write(line[1], data[rank])
                rank += 1
