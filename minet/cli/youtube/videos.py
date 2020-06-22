# =============================================================================
# Minet Youtube Videos CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving metadata about
# the given Youtube videos using Google's APIs.
#
import time
import casanova
from tqdm import tqdm
from minet.cli.youtube.utils import seconds_to_midnight_pacific_time
from minet.cli.utils import die
from minet.utils import create_pool, request_json, gen_chunks
from ural.youtube import (
    extract_video_id_from_youtube_url,
    is_youtube_video_id,
    is_youtube_url
)

URL_TEMPLATE = 'https://www.googleapis.com/youtube/v3/videos?id=%(list_id)s&key=%(key)s&part=snippet,statistics,contentDetails'

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
    'no_stat_likes',
    'duration',
    'caption'
]


def get_data(data_json):
    data_indexed = {}

    for element in data_json['items']:

        no_stat_likes = ''
        video_id = element['id']
        snippet = element['snippet']
        content_details = element['contentDetails']
        stat = element['statistics']

        published_at = snippet['publishedAt']
        channel_id = snippet['channelId']
        channel_title = snippet['channelTitle']
        title = snippet['title']
        description = snippet['description']

        duration = content_details['duration']
        caption = content_details['caption']

        view_count = stat.get('viewCount', None)
        like_count = stat.get('likeCount', None)
        dislike_count = stat.get('dislikeCount', None)
        favorite_count = stat.get('favoriteCount', None)
        comment_count = stat.get('commentCount', None)

        if not like_count:
            no_stat_likes = '1'

        data = [
            video_id,
            published_at,
            channel_id,
            title, description,
            channel_title,
            view_count,
            like_count,
            dislike_count,
            favorite_count,
            comment_count,
            no_stat_likes,
            duration,
            caption
        ]

        data_indexed[video_id] = data

    return data_indexed


# def gen_chunks(enricher):
#     chunk = []

#     for num, line in enumerate(enricher):

#         url_data = line[enricher.pos]
#         video_id = None

#         if len(chunk) == 50:
#             yield chunk
#             chunk.clear()

#         if is_youtube_video_id(url_data):
#             video_id = url_data

#         elif is_youtube_url(url_data):
#             video_id = extract_video_id_from_youtube_url(url_data)

#         chunk.append((video_id, line))

#     yield chunk


def videos_action(namespace, output_file):

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        add=REPORT_HEADERS,
        keep=namespace.select
    )

    loading_bar = tqdm(
        desc='Retrieving',
        dynamic_ncols=True,
        unit=' videos',
    )

    http = create_pool()
    column = namespace.column

    for chunk in gen_chunks(column, enricher, 50):

        for row in chunk:
            ytb_data = row[0][0]
            video_id = None
            if is_youtube_video_id(ytb_data):
                video_id = ytb_data
            elif is_youtube_url(ytb_data):
                video_id = extract_video_id_from_youtube_url(ytb_data)

            row[0][0] = video_id

        all_ids = [row[0][0] for row in chunk if row[0][0]]
        list_id = ",".join(all_ids)

        url = URL_TEMPLATE % {'list_id': list_id, 'key': namespace.key}
        err, response, result = request_json(http, url)

        if err:
            die(err)
        elif response.status == 403:
            time.sleep(seconds_to_midnight_pacific_time())
            continue
        elif response.status >= 400:
            die(response.status)

        data = get_data(result)

        not_available = []

        id_available = set(data)
        not_available = set(all_ids).difference(id_available)

        loading_bar.update(len(chunk))

        line_empty = []

        for item in chunk:
            video_id, line = item

            video_id = video_id[0]

            if video_id is None:
                enricher.writerow(line)

            elif video_id in not_available:
                line_empty = [video_id] + [''] * (len(REPORT_HEADERS) - 1)
                enricher.writerow(line, line_empty)

            else:
                enricher.writerow(line, data[video_id])
