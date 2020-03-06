# =============================================================================
# Minet Youtube Videos CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving metadata about
# the given Youtube videos using Google's APIs.
#
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
    'comment_count'
]


def get_data(data_json, no):
    data = {}
    snippet = {}
    stat = {}
    items = []
    elements = []
    num = 0

    elements = data_json['items']

    for el in elements:
        if (num + 1) in no:
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

        video_id = el['id']
        snippet = el['snippet']
        stat = el['statistics']
        print(stat)

        published_at = snippet['publishedAt']
        channel_id = snippet['channelId']
        channel_title = snippet['channelTitle']
        title = snippet['title']
        description = snippet['description']

        view_count = stat['viewCount']
        like_count = stat['likeCount']
        dislike_count = stat['dislikeCount']
        favorite_count = stat['favoriteCount']
        comment_count = stat['commentCount']

        liste = [video_id, published_at, channel_id, title, description, channel_title, view_count, like_count, dislike_count, favorite_count, comment_count]
        data[num] = liste

    return data


def gen_chunks(enricher):

    id = []
    li = []
    index = []
    chunk = (id, li, index)

    for num, line in enumerate(enricher):
        url_data = line[enricher.pos]

        if len(id) == 50:
            yield chunk
            chunk.clear()

        if is_youtube_video_id(url_data):
            id.append(url_data)

        elif is_youtube_url(url_data):
            video_id = extract_video_id_from_youtube_url(url_data)

            if video_id:
                id.append(video_id)
            else:
                id.append(None)
                index.append(num)

        li.append(line)

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

    row_count = 0

    for line in enricher:
        row_count += 1

        gen = gen_chunks(enricher)
        chunk = next(gen)

        no = []
        for i in chunk[2]:
            no.append(i)

        list_id = ",".join(chunk[0])

        url = URL_TEMPLATE % {'list_id': list_id[:-1], 'key': namespace.key}
        print(url)
        http = create_pool()
        err, response, result = request_json(http, url)

        if err:
            die(err)
        elif response.status == 403:
            # limite du quota
            pass

        elif response.status >= 400:
            die(response.status)

        data = get_data(result, no)

        loading_bar.update(len(chunk[0]))

        for n, info in enumerate(chunk[1]):
            for x, y in data.items():
                if x == n:
                    enricher.write(info, y)
                elif n in no:
                    enricher.write_empty(info)
                    break
