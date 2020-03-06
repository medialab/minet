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
    'comment_count',
    'no_stat_likes'
]


def get_data(data_json):
    data = {}
    snippet = {}
    stat = {}
    items = []
    elements = []
    num = 0
    no_stat_likes = ''

    elements = data_json['items']

    for num, el in enumerate(elements):

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

        liste = [video_id, published_at, channel_id, title, description, channel_title, view_count, like_count, dislike_count, favorite_count, comment_count, no_stat_likes]
        data[num] = liste

    return data


def gen_chunks(enricher):
    chunk = []

    for num, line in enumerate(enricher):
        index = 0

        url_data = line[enricher.pos]

        if len(chunk) == 50:
            yield chunk
            chunk.clear()

        if is_youtube_video_id(url_data):
            video_id = url_data

        elif is_youtube_url(url_data):
            video_id = extract_video_id_from_youtube_url(url_data)

            if not video_id:
                index = num

        tup = (video_id, line, index)
        chunk.append(tup)

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

        v_id = []
        for i in chunk:
            if i[0]:
                v_id.append(i[0])
            else:
                enricher.write_empty(i[1])

        list_id = ",".join(v_id)

        url = URL_TEMPLATE % {'list_id': list_id, 'key': namespace.key}
        http = create_pool()
        err, response, result = request_json(http, url)

        if err:
            die(err)
        elif response.status == 403:
            # limite du quota
            pass

        elif response.status >= 400:
            die(response.status)

        data = get_data(result)

        loading_bar.update(len(chunk))

        for n, info in enumerate(chunk):
            for x, y in data.items():
                if x == n:
                    enricher.write(info[1], y)

