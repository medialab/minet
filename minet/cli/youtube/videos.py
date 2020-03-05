# =============================================================================
# Minet Youtube Videos CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving metadata about
# the given Youtube videos using Google's APIs.
#

import time
from tqdm import tqdm
from minet.cli.utils import CSVEnricher, die
from minet.utils import create_pool, request_json
from ural import force_protocol
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
    'comment_count'
]


def get_data(data_json, no):
    data = {}
    snippet = {}
    stat = {}
    items = []
    elements = []
    num = 0

    for key, val in data_json.items():
        if key == 'items':
            elements = val

    for el in elements:
        if (num+1) in no:
            num += 2
        else:
            num += 1

        liste = []
        video_id = 0
        published_at = ''
        channel_id = 0
        title = ''
        description = ''
        channel_title = ''
        view_count = 0
        like_count = 0
        dislike_count = 0
        favorite_count = 0
        comment_count = 0

        for k, v in el.items():
            if k == 'id':
                video_id = v
            if k == 'snippet':
                snippet = v
            if k == 'statistics':
                stat = v

        for a, b in snippet.items():
            if a == 'publishedAt':
                published_at = b
            if a == 'channelId':
                channel_id = b
            if a == 'channelTitle':
                channel_title = b
            if a == 'title':
                title = b
            if a == 'description':
                description = b

        for st, nb in stat.items():
            if st == 'viewCount':
                view_count = nb
            if st == 'likeCount':
                like_count = nb
            if st == 'dislikeCount':
                dislike_count = nb
            if st == 'favoriteCount':
                favorite_count = nb
            if st == 'commentCount':
                comment_count = nb

        liste = [video_id, published_at, channel_id, title, description, channel_title, view_count, like_count, dislike_count, favorite_count, comment_count]
        data[num] = liste

    return data


def gen_chunks(enricher):
    chunk = []
    li = []
    index = []
    num = 0

    for line in enricher:
        num += 1
        url_data = line[enricher.pos]

        if len(chunk) == 50:
            yield chunk, li, index
            chunk.clear()

        if is_youtube_video_id(url_data):
            chunk.append(url_data)

        elif is_youtube_url(url_data):
            video_id = extract_video_id_from_youtube_url(url_data)

            if video_id:
                chunk.append(video_id)
            else:
                chunk.append(0)
                index.append(num)

        li.append(line)

    yield chunk, li, index


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
        unit=' chunks',
    )

    row_count = 0

    for line in enricher:
        row_count += 1

        gen = gen_chunks(enricher)
        chunk, li, index = next(gen)

        no = []
        for i in index:
            no.append(i)

        list_id = ''
        for id in chunk:
            if id != 0:
                list_id = list_id + id + ','

        url = URL_TEMPLATE % {'list_id': list_id[:-1], 'key': namespace.key}
        print(url)
        http = create_pool()
        err, response, result = request_json(http, url)

        if err:
            die(err)
        elif response.status == 403:
            # limite du quota

        elif response.status >= 400:
            die(response.status)

        data = get_data(result, no)

        loading_bar.update()

        n = 0
        for info in li:
            n += 1
            for x, y in data.items():
                if x == n:
                    enricher.write(info, y)
                elif n in no:
                    enricher.write_empty(info)
                    break



